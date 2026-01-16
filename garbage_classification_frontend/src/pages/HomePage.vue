<template>
  <div class="container mt-5">
    <div class="row">
      <div class="col-md-8 offset-md-2">
        <div class="card">
          <div class="card-body">
            <h2>首页</h2>
            <p class="lead">欢迎使用垃圾分类智能识别系统</p>

            <div class="row mt-4">
              <div class="col-md-6 mb-3">
                <div class="card text-center h-100">
                  <div class="card-body">
                    <i class="bi bi-cloud-upload" style="font-size: 3rem; color: #28a745"></i>
                    <h5 class="card-title mt-3">上传图片</h5>
                    <p class="card-text">上传包含垃圾的图片，系统会自动识别垃圾类别。</p>
                    <router-link to="/user/detect" v-if="isLoggedIn" class="btn btn-success">开始识别</router-link>
                    <router-link to="/login" v-else class="btn btn-success">登录后开始</router-link>
                  </div>
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <div class="card text-center h-100">
                  <div class="card-body">
                    <i class="bi bi-graph-up" style="font-size: 3rem; color: #0dcaf0"></i>
                    <h5 class="card-title mt-3">查看历史</h5>
                    <p class="card-text">查看您所有的识别历史记录和统计信息。</p>
                    <router-link to="/user/history" v-if="isLoggedIn" class="btn btn-info">查看历史</router-link>
                    <router-link to="/login" v-else class="btn btn-info">登录后查看</router-link>
                  </div>
                </div>
              </div>
            </div>

            <div class="row mt-4">
              <div class="col-md-6 mb-3">
                <div class="card text-center h-100">
                  <div class="card-body">
                    <i class="bi bi-info-circle" style="font-size: 3rem; color: #6c757d"></i>
                    <h5 class="card-title mt-3">了解更多</h5>
                    <p class="card-text">了解垃圾分类标准和系统功能介绍。</p>
                    <router-link to="/about" class="btn btn-secondary">详细了解</router-link>
                  </div>
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <div class="card text-center h-100">
                  <div class="card-body">
                    <i class="bi bi-gear" style="font-size: 3rem; color: #764ba2"></i>
                    <h5 class="card-title mt-3">个人资料</h5>
                    <p class="card-text">管理您的账户和个人信息。</p>
                    <router-link to="/user/profile" v-if="isLoggedIn" class="btn btn-primary">前往</router-link>
                    <router-link to="/login" v-else class="btn btn-primary">登录后管理</router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuth } from '../composables/useAuth'

const { isLoggedIn } = useAuth()
</script>

<style scoped>
.card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.btn {
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
}
</style>
