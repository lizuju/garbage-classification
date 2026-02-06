<template>
  <transition name="fade">
    <div v-if="isOpen" class="modal-backdrop-blur" @click.self="handleBackdropClick">
      <transition name="zoom-fade">
        <div 
          v-if="isOpen" 
          :class="['modal-container', 'card', 'card-glass', modalType === 'profile' ? 'modal-profile' : '']"
        >
          <!-- Close Button -->
          <!-- Close Button -->
          <CommonButton 
            theme="glass-dark" 
            circle 
            size="md" 
            class="modal-close-btn" 
            @click="closeModal" 
            aria-label="关闭"
          >
            <i class="bi bi-x-lg"></i>
          </CommonButton>

          <!-- Login Form -->
          <div v-if="modalType === 'login'" class="modal-content-inner">
            <div class="card-body p-4 p-md-5">
              <h3 class="card-title mb-2 text-center">登录</h3>
              <p class="text-center text-muted mb-4">登录您的账户以使用所有功能</p>

              <div v-if="loginLoading" class="text-center my-4">
                <div class="spinner-border text-success" role="status">
                  <span class="visually-hidden">加载中...</span>
                </div>
                <p class="mt-2 text-muted">正在处理请求...</p>
              </div>

              <div v-if="loginMessage" :class="`alert alert-${loginMessageType} mb-3`" role="alert">
                {{ loginMessage }}
              </div>

              <form @submit.prevent="handleLogin">
                <div class="mb-3">
                  <label for="modal-login-id" class="form-label">用户名或邮箱</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-person-circle"></i></span>
                    <input
                      id="modal-login-id"
                      v-model="loginForm.login_id"
                      type="text"
                      class="form-control"
                      required
                      :disabled="loginLoading"
                    />
                  </div>
                </div>

                <div class="mb-3">
                  <label for="modal-login-password" class="form-label">密码</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-lock"></i></span>
                    <input
                      id="modal-login-password"
                      v-model="loginForm.password"
                      type="password"
                      class="form-control"
                      required
                      :disabled="loginLoading"
                    />
                  </div>
                </div>

                <div class="mb-3 form-check">
                  <input type="checkbox" class="form-check-input" id="modal-remember-me">
                  <label class="form-check-label" for="modal-remember-me">记住我</label>
                </div>

                <CommonButton 
                  native-type="submit" 
                  theme="success" 
                  size="md" 
                  class="w-100" 
                  :disabled="loginLoading"
                >
                  <span v-if="!loginLoading">登录</span>
                  <span v-else>
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    登录中...
                  </span>
                </CommonButton>
              </form>

              <p class="text-center mt-3">
                没有账号？<a href="#" @click.prevent="switchToRegister" class="text-success">立即注册</a>
              </p>
            </div>
          </div>

          <!-- Register Form -->
          <div v-else-if="modalType === 'register'" class="modal-content-inner">
            <div class="card-body p-4 p-md-5">
              <h3 class="card-title mb-2 text-center">注册</h3>
              <p class="text-center text-muted mb-4">创建账户以使用垃圾分类识别系统</p>

              <div v-if="registerLoading" class="text-center my-4">
                <div class="spinner-border text-success" role="status">
                  <span class="visually-hidden">加载中...</span>
                </div>
                <p class="mt-2 text-muted">正在处理请求...</p>
              </div>

              <div v-if="registerMessage" :class="`alert alert-${registerMessageType} mb-3`" role="alert">
                {{ registerMessage }}
              </div>

              <form @submit.prevent="handleRegister">
                <div class="mb-3">
                  <label for="modal-register-username" class="form-label">用户名</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-person"></i></span>
                    <input 
                      id="modal-register-username"
                      v-model="registerForm.username" 
                      type="text" 
                      class="form-control" 
                      required
                      :disabled="registerLoading"
                    />
                  </div>
                  <small class="form-text text-muted">
                    用户名长度为3-20个字符, 只能包含字母、数字和下划线
                  </small>
                </div>

                <div class="mb-3">
                  <label for="modal-register-email" class="form-label">邮箱</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                    <input
                      id="modal-register-email"
                      v-model="registerForm.email"
                      type="email"
                      class="form-control"
                      required
                      :disabled="registerLoading"
                    />
                  </div>
                </div>

                <div class="mb-3">
                  <label for="modal-register-password" class="form-label">密码</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-lock"></i></span>
                    <input
                      id="modal-register-password"
                      v-model="registerForm.password"
                      type="password"
                      class="form-control"
                      required
                      :disabled="registerLoading"
                    />
                  </div>
                  <div class="d-flex justify-content-between mt-1">
                    <small class="form-text text-muted">密码长度至少为8个字符</small>
                    <div v-if="registerForm.password.length > 0 && registerForm.password.length < 8" class="text-danger small fw-bold">
                      <i class="bi bi-exclamation-circle me-1"></i>长度不足
                    </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="modal-register-confirm-password" class="form-label">确认密码</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-lock-fill"></i></span>
                    <input
                      id="modal-register-confirm-password"
                      v-model="registerForm.confirmPassword"
                      type="password"
                      class="form-control"
                      required
                      :disabled="registerLoading"
                    />
                  </div>
                </div>

                <div class="mb-3 form-check">
                  <input type="checkbox" class="form-check-input" id="modal-terms" v-model="registerForm.acceptTerms" required>
                  <label class="form-check-label" for="modal-terms">我已阅读并同意服务条款和隐私政策</label>
                </div>

                <CommonButton 
                  native-type="submit" 
                  theme="success" 
                  size="md" 
                  class="w-100" 
                  :disabled="registerLoading"
                >
                  <span v-if="!registerLoading">注册</span>
                  <span v-else>
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    注册中...
                  </span>
                </CommonButton>
              </form>

              <p class="text-center mt-3">
                已有账号？<a href="#" @click.prevent="switchToLogin" class="text-success">立即登录</a>
              </p>
            </div>
          </div>

          <!-- Profile Form (embedded from ProfilePage logic) -->
          <div v-else-if="modalType === 'profile'" class="modal-content-inner">
            <div class="bg-success" style="height: 6px; border-radius: 24px 24px 0 0;"></div>
            <ProfileContent @close="closeModal" />
          </div>
        </div>
      </transition>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { useAuthModal } from '../composables/useAuthModal'
import ProfileContent from './ProfileContent.vue'
import CommonButton from './CommonButton.vue'
import '../styles/components/modal.css'
import '../styles/components/card.css'
import '../styles/components/common-button.css'

const router = useRouter()
const { login, register } = useAuth()
const { isOpen, modalType, closeModal, switchToLogin, switchToRegister } = useAuthModal()

// Login form state
const loginForm = ref({ login_id: '', password: '' })
const loginMessage = ref('')
const loginMessageType = ref('')
const loginLoading = ref(false)

// Register form state
const registerForm = ref({ 
  username: '', 
  email: '', 
  password: '', 
  confirmPassword: '',
  acceptTerms: false
})
const registerMessage = ref('')
const registerMessageType = ref('')
const registerLoading = ref(false)

// Reset forms when modal closes
watch(isOpen, (newVal) => {
  if (!newVal) {
    loginForm.value = { login_id: '', password: '' }
    loginMessage.value = ''
    registerForm.value = { username: '', email: '', password: '', confirmPassword: '', acceptTerms: false }
    registerMessage.value = ''
  }
})

const handleBackdropClick = () => {
  closeModal()
}

const handleLogin = async () => {
  if (!loginForm.value.login_id || !loginForm.value.password) {
    loginMessage.value = '请填写所有字段'
    loginMessageType.value = 'warning'
    return
  }

  loginLoading.value = true
  try {
    await login(loginForm.value.login_id, loginForm.value.password)
    loginMessage.value = '登录成功！'
    loginMessageType.value = 'success'
    setTimeout(() => {
      closeModal()
      // Stay on current page instead of redirecting
      // router.push('/user/detect') 
    }, 800)
  } catch (error) {
    loginMessage.value = error.message || '登录失败，请重试'
    loginMessageType.value = 'danger'
  } finally {
    loginLoading.value = false
  }
}

const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.email || !registerForm.value.password) {
    registerMessage.value = '请填写所有字段'
    registerMessageType.value = 'warning'
    return
  }

  if (registerForm.value.password.length < 8) {
    registerMessage.value = '密码长度至少为 8 个字符'
    registerMessageType.value = 'warning'
    return
  }

  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    registerMessage.value = '两次输入的密码不一致'
    registerMessageType.value = 'warning'
    return
  }

  registerLoading.value = true
  try {
    await register(registerForm.value.username, registerForm.value.email, registerForm.value.password)
    registerMessage.value = '注册成功！请登录'
    registerMessageType.value = 'success'
    setTimeout(() => {
      switchToLogin()
      registerMessage.value = ''
    }, 1000)
  } catch (error) {
    registerMessage.value = error.message || '注册失败，请重试'
    registerMessageType.value = 'danger'
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.modal-content-inner {
  max-height: 95vh;
  overflow-y: auto;
}
</style>
