import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { useAuthModal } from '../composables/useAuthModal'

// 页面组件
import HomePage from '../pages/HomePage.vue'
import AboutPage from '../pages/AboutPage.vue'
import RecycleMapPage from '../pages/RecycleMapPage.vue'
import DetectPage from '../pages/DetectPage.vue'
import HistoryPage from '../pages/HistoryPage.vue'
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
    // Redirect to home and open login modal
    redirect: '/',
    meta: { openModal: 'login' }
  },
  {
    path: '/register',
    name: 'Register',
    // Redirect to home and open register modal
    redirect: '/',
    meta: { openModal: 'register' }
  },
  {
    path: '/about',
    name: 'About',
    component: AboutPage,
  },
  {
    path: '/recycle-map',
    name: 'RecycleMap',
    component: RecycleMapPage,
    meta: { requiresAuth: true },
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
    // Redirect to previous route and open profile modal
    redirect: (to) => {
      return { path: '/' }
    },
    meta: { requiresAuth: true, openModal: 'profile' }
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
  scrollBehavior(to, from, savedPosition) {
    // 禁用浏览器自动滚动恢复
    if ('scrollRestoration' in window.history) {
      window.history.scrollRestoration = 'manual'
    }

    // 优先处理 hash 锚点（Home 页内部或跨页面）
    if (to.hash) {
      return new Promise(resolve => {
        // 等 DOM 渲染稳定后再滚动
        setTimeout(() => {
          const el = document.querySelector(to.hash)
          if (el) {
            resolve({
              el: to.hash,
              behavior: 'smooth'
            })
          } else {
            resolve({ top: 0 })
          }
        }, 100) // 延迟 100ms，可以根据页面复杂度调整
      })
    }

    // 跨页面跳转（例如 Home → About），没有 hash，滚到顶部
    if (from.path !== to.path) {
      return new Promise(resolve => {
        // 等 DOM 渲染稳定
        setTimeout(() => {
          resolve({ top: 0 })
        }, 50) // 小延迟，页面刚渲染完就滚动
      })
    }

    // 浏览器前进/后退，保持滚动位置
    if (savedPosition) {
      return savedPosition
    }

    // 默认滚动到顶部
    return { top: 0 }
  }
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
    // Open login modal instead of redirecting to login page
    const { openLogin } = useAuthModal()
    openLogin()
    next('/')
    return
  }

  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin && (!user.value || !user.value.is_admin)) {
    next('/')
    return
  }

  next()
})

// Handle modal opening after navigation
router.afterEach((to, from) => {
  if (to.meta.openModal) {
    const { openLogin, openRegister, openProfile } = useAuthModal()

    // Delay modal opening slightly to ensure DOM is ready
    setTimeout(() => {
      if (to.meta.openModal === 'login') {
        openLogin()
      } else if (to.meta.openModal === 'register') {
        openRegister()
      } else if (to.meta.openModal === 'profile') {
        openProfile()
      }
    }, 100)
  }
})

export default router
