<template>
  <div id="app" class="d-flex flex-column min-vh-100">
    <Navbar />
    <main class="flex-grow-1">
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuth } from './composables/useAuth'
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'

// 导入图标文件，让 Vite 处理它们的路径（包含哈希）
import favicon from './assets/icons/favicon.ico'
import appleIcon from './assets/icons/apple-touch-icon.png'
import appleIconPrecomposed from './assets/icons/apple-touch-icon-precomposed.png'

// 在应用启动时初始化认证状态
const { initAuth } = useAuth()

onMounted(() => {
  initAuth()
  
  // 动态注入图标链接到 head
  const updateIcon = (rel, href) => {
    let link = document.querySelector(`link[rel="${rel}"]`)
    if (!link) {
      link = document.createElement('link')
      link.rel = rel
      document.head.appendChild(link)
    }
    link.href = href
  }

  updateIcon('icon', favicon)
  updateIcon('apple-touch-icon', appleIcon)
  updateIcon('apple-touch-icon-precomposed', appleIconPrecomposed)
})
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  min-height: 100vh;
}

main {
  flex: 1;
}

.min-vh-100 {
  min-height: 100vh;
}

.d-flex {
  display: flex;
}

.flex-column {
  flex-direction: column;
}

.flex-grow-1 {
  flex: 1;
}
</style>
