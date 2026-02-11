import { useAuth } from './useAuth'

export function useApi() {
  const API_BASE = 'http://localhost:5001'
  const { getHeaders } = useAuth()

  // 处理 API 响应，如果是 401 则自动跳转到登录
  const handleResponse = async (response) => {
    if (response.status === 401) {
      // Token 过期或无效，清除本地存储并需要重新登录
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
      throw new Error('会话已过期，请重新登录')
    }
    return response
  }

  // 将图片 URL 转换为 base64 数据 URL（支持带认证的图片加载）
  const convertImageToBase64 = async (imageUrl) => {
    try {
      const response = await fetch(imageUrl, { headers: getHeaders() })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)

      const blob = await response.blob()
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result)
        reader.onerror = () => {
          console.error('FileReader error')
          resolve(null)
        }
        reader.readAsDataURL(blob)
      })
    } catch (error) {
      console.error('转换图片失败:', imageUrl, error)
      return null
    }
  }

  const detect = async (file) => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const headers = getHeaders()
      // FormData 会自动设置 Content-Type，删除手动设置
      delete headers['Content-Type']

      const response = await fetch(`${API_BASE}/api/detect`, {
        method: 'POST',
        headers,
        body: formData,
      })

      await handleResponse(response)

      const data = await response.json()
      if (data.status === 'success') {
        // 将结果图片 URL 转换为 base64（支持认证）
        if (data.result_url) {
          const fullUrl = `${API_BASE}${data.result_url}`
          data.result_url_base64 = await convertImageToBase64(fullUrl)
        }
        return data
      }
      throw new Error(data.message || '检测失败')
    } catch (error) {
      console.error('检测失败:', error)
      throw error
    }
  }

  const detectBatch = async (files) => {
    const runFallbackBySingleDetect = async () => {
      const items = []
      let successCount = 0
      for (const file of files) {
        try {
          const result = await detect(file)
          items.push({
            ...result,
            filename: file.name,
            status: 'success',
          })
          successCount += 1
        } catch (error) {
          items.push({
            status: 'error',
            filename: file.name,
            message: error.message || '识别失败',
          })
        }
      }

      const failedCount = files.length - successCount
      if (successCount === 0) {
        throw new Error('批量识别失败')
      }

      return {
        status: 'success',
        message: `批量识别完成：成功 ${successCount} 张，失败 ${failedCount} 张`,
        total: files.length,
        success_count: successCount,
        failed_count: failedCount,
        items,
      }
    }

    try {
      if (!Array.isArray(files) || files.length === 0) {
        throw new Error('请至少选择一张图片')
      }

      const formData = new FormData()
      files.forEach((file) => {
        formData.append('files', file)
      })

      const headers = getHeaders()
      delete headers['Content-Type']

      const response = await fetch(`${API_BASE}/api/detect/batch`, {
        method: 'POST',
        headers,
        body: formData,
      })

      await handleResponse(response)

      let data = null
      try {
        data = await response.json()
      } catch (error) {
        throw new Error('批量接口返回格式异常')
      }

      if (!response.ok) {
        throw new Error(data?.message || `批量检测失败 (HTTP ${response.status})`)
      }

      if (data.status !== 'success') {
        throw new Error(data.message || '批量检测失败')
      }

      const items = Array.isArray(data.items) ? data.items : []
      for (const item of items) {
        if (item.status === 'success' && item.result_url) {
          const fullUrl = `${API_BASE}${item.result_url}`
          item.result_url_base64 = await convertImageToBase64(fullUrl)
        }
      }

      return data
    } catch (error) {
      const isNetworkError = error instanceof TypeError || /Failed to fetch/i.test(String(error?.message || ''))
      if (isNetworkError) {
        console.warn('批量接口不可用，已自动降级为逐张识别:', error)
        return runFallbackBySingleDetect()
      }
      console.error('批量检测失败:', error)
      throw error
    }
  }

  const getHistory = async (page = 1, pageSize = 10) => {
    try {
      const response = await fetch(
        `${API_BASE}/api/user/history?page=${page}&page_size=${pageSize}`,
        { headers: getHeaders() }
      )

      await handleResponse(response)

      const data = await response.json()
      if (data.status === 'success') {
        return data
      }
      throw new Error(data.message || '获取历史失败')
    } catch (error) {
      console.error('获取历史失败:', error)
      throw error
    }
  }

  const deleteHistory = async (historyId) => {
    try {
      const response = await fetch(`${API_BASE}/api/user/history/${historyId}`, {
        method: 'DELETE',
        headers: getHeaders(),
      })

      await handleResponse(response)

      const data = await response.json()
      if (data.status === 'success') {
        return data
      }
      throw new Error(data.message || '删除失败')
    } catch (error) {
      console.error('删除历史失败:', error)
      throw error
    }
  }

  const getAdminStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/admin/stats`, {
        headers: getHeaders(),
      })

      await handleResponse(response)

      const data = await response.json()
      if (data.status === 'success') {
        return data
      }
      throw new Error(data.message || '获取统计失败')
    } catch (error) {
      console.error('获取管理员统计失败:', error)
      throw error
    }
  }

  const getAdminUsers = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/admin/users`, {
        headers: getHeaders(),
      })

      await handleResponse(response)

      const data = await response.json()
      if (data.status === 'success') {
        return data
      }
      throw new Error(data.message || '获取用户列表失败')
    } catch (error) {
      console.error('获取管理员用户列表失败:', error)
      throw error
    }
  }

  const getAdminUserDetail = async (userId) => {
    try {
      const response = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
        headers: getHeaders(),
      })

      await handleResponse(response)

      const data = await response.json()
      if (data.status === 'success') {
        return data
      }
      throw new Error(data.message || '获取用户详情失败')
    } catch (error) {
      console.error('获取管理员用户详情失败:', error)
      throw error
    }
  }

  const updateAdminUser = async (userId, payload) => {
    try {
      const response = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(payload),
      })

      await handleResponse(response)

      const data = await response.json()
      if (data.status === 'success') {
        return data
      }
      throw new Error(data.message || '更新用户失败')
    } catch (error) {
      console.error('更新管理员用户失败:', error)
      throw error
    }
  }

  const updateAdminUserStatus = async (userId, isActive) => {
    try {
      const response = await fetch(`${API_BASE}/api/admin/users/${userId}/status`, {
        method: 'PATCH',
        headers: getHeaders(),
        body: JSON.stringify({ is_active: isActive }),
      })

      await handleResponse(response)

      const data = await response.json()
      if (data.status === 'success') {
        return data
      }
      throw new Error(data.message || '更新用户状态失败')
    } catch (error) {
      console.error('更新管理员用户状态失败:', error)
      throw error
    }
  }

  const getAdminLogs = async (page = 1, perPage = 20) => {
    try {
      const response = await fetch(`${API_BASE}/api/admin/logs?page=${page}&per_page=${perPage}`, {
        headers: getHeaders(),
      })

      await handleResponse(response)

      const data = await response.json()
      if (data.status === 'success') {
        return data
      }
      throw new Error(data.message || '获取系统日志失败')
    } catch (error) {
      console.error('获取系统日志失败:', error)
      throw error
    }
  }

  const exportAdminData = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/admin/export`, {
        headers: getHeaders(),
      })

      await handleResponse(response)

      const data = await response.json()
      if (data.status === 'success') {
        return data.export_data
      }
      throw new Error(data.message || '导出数据失败')
    } catch (error) {
      console.error('导出管理员数据失败:', error)
      throw error
    }
  }

  return {
    detect,
    detectBatch,
    getHistory,
    deleteHistory,
    getAdminStats,
    getAdminUsers,
    getAdminUserDetail,
    updateAdminUser,
    updateAdminUserStatus,
    getAdminLogs,
    exportAdminData,
  }
}
