import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'

// 页面组件
import HomePage from '../pages/HomePage.vue'
import LoginPage from '../pages/LoginPage.vue'
import RegisterPage from '../pages/RegisterPage.vue'
import AboutPage from '../pages/AboutPage.vue'
import DetectPage from '../pages/DetectPage.vue'
import HistoryPage from '../pages/HistoryPage.vue'
import ProfilePage from '../pages/ProfilePage.vue'
import AdminPage from '../pages/AdminPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
  },
  {
    path: '/about',
    name: 'About',
    component: AboutPage,
  },
  {
    path: '/user/detect',
    name: 'Detect',
    component: DetectPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/user/history',
    name: 'History',
    component: HistoryPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/user/profile',
    name: 'Profile',
    component: ProfilePage,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminPage,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守护：检查认证
router.beforeEach(async (to, from, next) => {
  const { user, isLoggedIn, getCurrentUser } = useAuth()

  // 首次访问时检查用户状态
  if (!user.value && !isLoggedIn.value) {
    await getCurrentUser()
  }

  // 检查是否需要认证
  if (to.meta.requiresAuth && !isLoggedIn.value) {
    next('/login')
    return
  }

  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin && (!user.value || !user.value.is_admin)) {
    next('/')
    return
  }

  next()
})

export default router
