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
    getHistory,
    deleteHistory,
    getAdminStats,
    getAdminUsers,
    getAdminLogs,
    exportAdminData,
  }
}
