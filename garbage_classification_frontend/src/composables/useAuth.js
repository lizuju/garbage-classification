import { ref, computed, onMounted } from 'vue'

const user = ref(null)
const isLoading = ref(false)
const isLoggedIn = computed(() => !!user.value)
const token = ref(localStorage.getItem('auth_token') || null)

export function useAuth() {
  const API_BASE = 'http://localhost:5001'

  // 获取请求头，自动添加 JWT token
  const getHeaders = () => {
    const headers = { 'Content-Type': 'application/json' }
    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`
    }
    return headers
  }

  // 初始化时，如果有 token 则验证并获取用户信息
  const initAuth = async () => {
    if (token.value) {
      await getCurrentUser()
    }
  }

  const getCurrentUser = async () => {
    if (!token.value) {
      user.value = null
      return null
    }

    try {
      isLoading.value = true
      const response = await fetch(`${API_BASE}/api/user`, {
        headers: getHeaders(),
      })
      
      if (response.status === 401) {
        // Token 过期或无效
        token.value = null
        localStorage.removeItem('auth_token')
        user.value = null
        return null
      }

      const data = await response.json()
      
      if (data && data.status === 'success' && data.user) {
        user.value = data.user
        return data.user
      }
      user.value = null
      return null
    } catch (error) {
      console.error('获取当前用户失败:', error)
      user.value = null
      return null
    } finally {
      isLoading.value = false
    }
  }

  const login = async (login_id, password) => {
    try {
      const response = await fetch(`${API_BASE}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login_id, password }),
      })
      
      const data = await response.json()
      if (data.status === 'success' && data.user && data.token) {
        // 保存 token 到 localStorage
        token.value = data.token
        localStorage.setItem('auth_token', data.token)
        user.value = data.user
        return data
      }
      throw new Error(data.message || '登录失败')
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  const register = async (username, email, password) => {
    try {
      const response = await fetch(`${API_BASE}/api/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      })
      
      const data = await response.json()
      if (data.status === 'success') {
        return data
      }
      throw new Error(data.message || '注册失败')
    } catch (error) {
      console.error('注册失败:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      if (token.value) {
        await fetch(`${API_BASE}/api/logout`, {
          method: 'POST',
          headers: getHeaders(),
        })
      }
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      // 无论后端请求是否成功，都清除本地数据
      user.value = null
      token.value = null
      localStorage.removeItem('auth_token')
    }
  }

  const updateProfile = async (email, password, newPassword) => {
    try {
      const response = await fetch(`${API_BASE}/api/user/profile`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify({ email, password, new_password: newPassword }),
      })
      
      const data = await response.json()
      if (data.status === 'success') {
        if (data.user) user.value = data.user
        return data
      }
      throw new Error(data.message || '更新失败')
    } catch (error) {
      console.error('更新个人资料失败:', error)
      throw error
    }
  }

  return {
    user,
    isLoggedIn,
    isLoading,
    token,
    getCurrentUser,
    login,
    register,
    logout,
    updateProfile,
    initAuth,
    getHeaders,
  }
}
