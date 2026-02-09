<template>
  <div class="register-page-wrapper">
    <div class="container mt-5 mb-5">
      <div class="row justify-content-center">
        <div class="col-md-7">
          <div class="card card-glass">
            <div class="card-body p-5">
              <h3 class="card-title mb-2 text-center">注册</h3>
              <p class="text-center text-muted mb-4">创建账户以使用垃圾分类识别系统</p>

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
                  <label for="register-username" class="form-label">用户名</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-person"></i></span>
                    <input 
                      id="register-username"
                      v-model="formData.username" 
                      type="text" 
                      class="form-control" 
                      required
                      :disabled="isLoading"
                    />
                  </div>
                  <small class="form-text text-muted">
                    用户名长度为3-20个字符, 只能包含字母、数字和下划线
                  </small>
                </div>

                <div class="mb-3">
                  <label for="register-email" class="form-label">邮箱</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                    <input
                      id="register-email"
                      v-model="formData.email"
                      type="email"
                      class="form-control"
                      required
                      :disabled="isLoading"
                    />
                  </div>
                  <small class="form-text text-muted">
                    请输入有效的电子邮箱，用于账户验证和密码找回
                  </small>
                </div>

                <div class="mb-3">
                  <label for="register-password" class="form-label">密码</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-lock"></i></span>
                    <input
                      id="register-password"
                      v-model="formData.password"
                      type="password"
                      class="form-control"
                      required
                      :disabled="isLoading"
                    />
                  </div>
                  <div class="d-flex justify-content-between mt-1">
                    <small class="form-text text-muted">密码长度至少为8个字符，建议包含字母、数字和特殊字符</small>
                      <div v-if="formData.password.length > 0 && formData.password.length < 8" class="text-danger small fw-bold">
                        <i class="bi bi-exclamation-circle me-1"></i>长度不足
                      </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="register-confirm-password" class="form-label">确认密码</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-lock-fill"></i></span>
                    <input
                      id="register-confirm-password"
                      v-model="formData.confirmPassword"
                      type="password"
                      class="form-control"
                      required
                      :disabled="isLoading"
                    />
                  </div>
                </div>

                <div class="mb-3 form-check">
                  <input type="checkbox" class="form-check-input" id="terms" required>
                  <label class="form-check-label terms-links" for="terms">
                    我已阅读并同意
                    <a href="#" @click.prevent="openTerms">服务条款</a>
                    和
                    <a href="#" @click.prevent="openPrivacy">隐私政策</a>
                  </label>
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

    <TermsPrivacyModal :isOpen="showTerms" type="terms" @close="closeTerms" />
    <TermsPrivacyModal :isOpen="showPrivacy" type="privacy" @close="closePrivacy" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import TermsPrivacyModal from '../components/TermsPrivacyModal.vue'
import '../styles/pages/register.css'
import '../styles/components/card.css'

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
const showTerms = ref(false)
const showPrivacy = ref(false)

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

const openTerms = () => {
  showTerms.value = true
}

const closeTerms = () => {
  showTerms.value = false
}

const openPrivacy = () => {
  showPrivacy.value = true
}

const closePrivacy = () => {
  showPrivacy.value = false
}
</script>
