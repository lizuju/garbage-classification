<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">
      <router-link to="/" class="navbar-brand fw-bold">
        🗑️ 垃圾分类检测系统
      </router-link>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
              首页
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/about" class="nav-link" :class="{ active: $route.path === '/about' }">
              关于项目
            </router-link>
          </li>

          <!-- 未登录菜单 -->
          <template v-if="!isLoggedIn">
            <li class="nav-item">
              <a href="#" class="nav-link" @click.prevent="openLogin">
                登录
              </a>
            </li>
            <li class="nav-item">
              <a href="#" class="nav-link" @click.prevent="openRegister">
                注册
              </a>
            </li>
          </template>

          <!-- 已登录菜单 -->
          <template v-else>
            <!-- 用户菜单 -->
            <li class="nav-item">
              <router-link to="/user/detect" class="nav-link" :class="{ active: $route.path.includes('/user/detect') }">
                识别检测
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/user/history" class="nav-link" :class="{ active: $route.path.includes('/user/history') }">
                识别历史
              </router-link>
            </li>

            <!-- 管理员菜单 -->
            <li v-if="user?.is_admin" class="nav-item">
              <router-link to="/admin" class="nav-link" :class="{ active: $route.path.includes('/admin') }">
                📊 管理后台
              </router-link>
            </li>

            <!-- 个人菜单 -->
            <li class="nav-item dropdown">
              <a
                class="nav-link dropdown-toggle"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
              >
                👤 {{ user?.username }}
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li>
                  <a href="#" class="dropdown-item" @click.prevent="openProfile">
                    个人资料
                  </a>
                </li>
                <li>
                  <hr class="dropdown-divider" />
                </li>
                <li>
                  <a href="#" class="dropdown-item" @click.prevent="handleLogout">
                    登出
                  </a>
                </li>
              </ul>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { useAuthModal } from '../composables/useAuthModal'

const { user, isLoggedIn, logout } = useAuth()
const { openLogin, openRegister, openProfile } = useAuthModal()
const router = useRouter()

const handleLogout = async () => {
  try {
    await logout()
    router.push('/')
  } catch (error) {
    console.error('登出失败:', error)
  }
}
</script>

<style scoped>
.navbar-brand {
  font-size: 1.5rem;
  letter-spacing: 1px;
}

.nav-link {
  transition: color 0.3s ease;
  position: relative;
  margin-left: 0.5rem;
  margin-right: 0.5rem;
  cursor: pointer;
}

.nav-link:hover {
  color: #28a745 !important;
}

.nav-link.active {
  color: #28a745 !important;
  font-weight: 600;
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: #28a745;
}
</style>
