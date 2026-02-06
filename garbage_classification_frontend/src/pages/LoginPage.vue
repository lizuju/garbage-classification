<template>
  <div class="login-page-wrapper">
    <div class="container mt-5 mb-5">
      <div class="row justify-content-center">
        <div class="col-md-7">
          <div class="card card-glass">
            <div class="card-body p-5">
              <h3 class="card-title mb-2 text-center">登录</h3>
              <p class="text-center text-muted mb-4">登录您的账户以使用所有功能</p>

              <div v-if="isLoading" class="text-center my-4">
                <div class="spinner-border text-success" role="status">
                  <span class="visually-hidden">加载中...</span>
                </div>
                <p class="mt-2 text-muted">正在处理请求...</p>
              </div>

              <div v-if="message" :class="`alert alert-${messageType} mb-3`" role="alert">
                {{ message }}
              </div>

              <form @submit.prevent="handleSubmit">
                <div class="mb-3">
                  <label for="login-id" class="form-label">用户名或邮箱</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-person-circle"></i></span>
                    <input
                      id="login-id"
                      v-model="formData.login_id"
                      type="text"
                      class="form-control"
                      required
                      :disabled="isLoading"
                    />
                  </div>
                </div>

                <div class="mb-3">
                  <label for="login-password" class="form-label">密码</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-lock"></i></span>
                    <input
                      id="login-password"
                      v-model="formData.password"
                      type="password"
                      class="form-control"
                      required
                      :disabled="isLoading"
                    />
                  </div>
                </div>

                <div class="mb-3 form-check">
                    <input type="checkbox" class="form-check-input" id="remember-me">
                    <label class="form-check-label" for="remember-me">记住我</label>
                </div>

                <button type="submit" class="btn btn-success w-100" :disabled="isLoading">
                  <span v-if="!isLoading">登录</span>
                  <span v-else>
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    登录中...
                  </span>
                </button>
              </form>

              <p class="text-center mt-3">
                没有账号？<router-link to="/register">立即注册</router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import '../styles/pages/login.css'
import '../styles/components/card.css'

const router = useRouter()
const { login } = useAuth()

const formData = ref({
  login_id: '',
  password: '',
})

const message = ref('')
const messageType = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  if (!formData.value.login_id || !formData.value.password) {
    message.value = '请填写所有字段'
    messageType.value = 'warning'
    return
  }

  isLoading.value = true
  try {
    const result = await login(formData.value.login_id, formData.value.password)
    message.value = '登录成功！'
    messageType.value = 'success'
    setTimeout(() => {
      router.push('/user/detect')
    }, 1000)
  } catch (error) {
    message.value = error.message || '登录失败，请重试'
    messageType.value = 'danger'
  } finally {
    isLoading.value = false
  }
}
</script>