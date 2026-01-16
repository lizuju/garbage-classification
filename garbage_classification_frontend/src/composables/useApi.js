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

  return {
    detect,
    getHistory,
    deleteHistory,
    getAdminStats,
  }
}
