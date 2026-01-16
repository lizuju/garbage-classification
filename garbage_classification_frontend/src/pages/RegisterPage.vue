<template>
  <div class="container mt-5 mb-5">
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card shadow">
          <div class="card-body p-5">
            <h3 class="card-title mb-4 text-center">注册</h3>

            <div v-if="message" :class="`alert alert-${messageType} mb-3`" role="alert">
              {{ message }}
            </div>

            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label class="form-label">用户名</label>
                <input
                  v-model="formData.username"
                  type="text"
                  class="form-control"
                  required
                  :disabled="isLoading"
                />
              </div>

              <div class="mb-3">
                <label class="form-label">邮箱</label>
                <input
                  v-model="formData.email"
                  type="email"
                  class="form-control"
                  required
                  :disabled="isLoading"
                />
              </div>

              <div class="mb-3">
                <label class="form-label">密码</label>
                <input
                  v-model="formData.password"
                  type="password"
                  class="form-control"
                  required
                  :disabled="isLoading"
                />
                <small class="form-text text-muted">
                  密码长度至少为 8 个字符
                </small>
              </div>

              <div class="mb-3">
                <label class="form-label">确认密码</label>
                <input
                  v-model="formData.confirmPassword"
                  type="password"
                  class="form-control"
                  required
                  :disabled="isLoading"
                />
              </div>

              <button type="submit" class="btn btn-success w-100" :disabled="isLoading">
                <span v-if="!isLoading">注册</span>
                <span v-else>
                  <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  注册中...
                </span>
              </button>
            </form>

            <p class="text-center mt-3">
              已有账号？<router-link to="/login">立即登录</router-link>
            </p>
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

const router = useRouter()
const { register } = useAuth()

const formData = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const message = ref('')
const messageType = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  if (!formData.value.username || !formData.value.email || !formData.value.password) {
    message.value = '请填写所有字段'
    messageType.value = 'warning'
    return
  }

  if (formData.value.password.length < 8) {
    message.value = '密码长度至少为 8 个字符'
    messageType.value = 'warning'
    return
  }

  if (formData.value.password !== formData.value.confirmPassword) {
    message.value = '两次输入的密码不一致'
    messageType.value = 'warning'
    return
  }

  isLoading.value = true
  try {
    await register(formData.value.username, formData.value.email, formData.value.password)
    message.value = '注册成功！正在跳转登录...'
    messageType.value = 'success'
    setTimeout(() => {
      router.push('/login')
    }, 1000)
  } catch (error) {
    message.value = error.message || '注册失败，请重试'
    messageType.value = 'danger'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.card {
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-success {
  background-color: #28a745;
  border: none;
  padding: 0.6rem 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-success:hover {
  background-color: #218838;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
}

.form-control:focus {
  border-color: #28a745;
  box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
}

a {
  color: #28a745;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>
