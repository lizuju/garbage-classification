<template>
  <footer class="footer mt-5">
    <div class="container">
      <div class="row">
        <div class="col-md-6 mb-4">
          <h5>垃圾分类识别系统</h5>
          <p>基于YOLOv5的垃圾智能识别系统，帮助您正确分类垃圾，保护环境，共建绿色家园。</p>
        </div>
        <div class="col-md-3 mb-4">
          <h5>链接</h5>
          <ul class="list-unstyled">
            <li><router-link to="/">首页</router-link></li>
            <li><router-link to="/about">关于项目</router-link></li>
            <li><a href="#" @click.prevent="goProtected('/user/detect')">识别检测</a></li>
            <li><a href="#" @click.prevent="goProtected('/recycle-map')">回收地图</a></li>
            <li><a href="#" @click.prevent="goProtected('/user/history')">识别历史</a></li>
          </ul>
        </div>
        <div class="col-md-3 mb-4">
          <h5>联系我们</h5>
          <ul class="list-unstyled">
            <li><i class="bi bi-envelope me-2"></i> li2096870763@gmail.com</li>
            <li><i class="bi bi-telephone me-2"></i> +86 132 5054 1959</li>
          </ul>
        </div>
      </div>
      <hr />
      <div class="text-center">
        <p>&copy; {{ currentYear }} 垃圾分类识别系统. 保留所有权利.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { useAuthModal } from '../composables/useAuthModal'

const currentYear = ref(new Date().getFullYear())
const router = useRouter()
const { isLoggedIn } = useAuth()
const { openLogin } = useAuthModal()

const goProtected = (path) => {
  if (!isLoggedIn.value) {
    openLogin()
    return
  }
  router.push(path)
}
</script>

<style scoped>
footer a {
  color: #ecf0f1;
  text-decoration: none;
  transition: color 0.3s ease;
}

footer a:hover {
  color: #28a745;
}

footer h5 {
  color: white;
  margin-bottom: 15px;
  font-weight: 600;
}
</style>
