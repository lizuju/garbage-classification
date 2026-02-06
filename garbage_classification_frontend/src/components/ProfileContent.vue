<template>
  <div class="card-body p-4 p-md-5">
    <div class="text-center mb-4">
      <h3 class="card-title fw-bold">个人资料</h3>
      <p class="text-muted">管理您的账户信息和安全设置</p>
    </div>

    <form @submit.prevent="handleUpdate" class="mt-4">
      
      <div class="mb-3 p-3 bg-light rounded-3 mx-0">
        <label class="form-label fw-bold text-secondary small">用户名</label>
        <div class="input-group">
          <span class="input-group-text bg-light border-0"><i class="bi bi-person text-muted"></i></span>
          <input :value="user?.username" type="text" class="form-control bg-light border-0" disabled />
        </div>
      </div>

      <div class="mb-3 p-3 bg-light rounded-3 mx-0">
        <label for="profile-email" class="form-label fw-bold text-secondary small">邮箱地址</label>
        <div class="input-group">
          <span class="input-group-text bg-light border-0"><i class="bi bi-envelope text-muted"></i></span>
          <input id="profile-email" :value="user?.email" type="email" class="form-control border-0 bg-light" disabled />
        </div>
      </div>

      <div class="row g-1 mb-3 p-3 bg-light rounded-3 mx-0">
        <div class="col-sm-6">
          <div class="d-flex flex-column">
            <span class="form-label fw-bold text-secondary small">注册时间</span>
            <span class="fw-medium">{{ formattedDate }}</span>
          </div>
        </div>
        <div class="col-sm-6">
          <div class="d-flex flex-column">
            <span class="form-label fw-bold text-secondary small">账户类型</span>
            <div>
              <span :class="['role-label', user?.is_admin ? 'admin' : 'user']">
                {{ userTypeLabel }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <hr class="my-4 opacity-25">

      <h5 class="mb-4 fw-bold">
        <i class="bi bi-shield-lock me-2"></i>账户安全与更改
      </h5>

      <div v-if="isLoading" class="text-center my-4">
        <div class="spinner-border text-success" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
        <p class="mt-2 text-muted">正在处理请求...</p>
      </div>

      <transition name="zoom-fade">
        <div v-if="actionNotice" 
            :class="['alert', `alert-${noticeType}`, 'border-0', 'shadow-lg', 'text-center', 'py-2', 'mb-4']" 
            role="alert">
          <i :class="noticeType === 'success' ? 'bi bi-check-circle-fill' : 'bi bi-x-circle-fill'" class="me-2"></i>
          {{ actionNotice }}
        </div>
      </transition>

      <transition name="fade-slide">
        <div v-if="message" :class="`alert alert-${messageType} border-0 shadow-sm mb-4`" role="alert">
          {{ message }}
        </div>
      </transition>

      <div v-if="!isVerified" class="verification-zone p-4 border rounded-3 bg-light shadow-sm">
        <div class="mb-3">
          <label for="profile-current-password" class="form-label fw-bold text-secondary small">
            第一步：请输入当前密码验证身份 <span class="text-danger">*</span>
          </label>
          <div class="input-group">
            <span class="input-group-text bg-white"><i class="bi bi-lock"></i></span>
            <input 
              id="profile-current-password" 
              v-model="formData.password" 
              type="password" 
              class="form-control border-start-0" 
              placeholder="输入当前密码以解锁编辑"
              @keyup.enter="verifyCurrentPassword"
            />
            <CommonButton 
              theme="success" 
              size="md" 
              class="px-4" 
              @click="verifyCurrentPassword" 
              :disabled="isLoading"
            >
              {{ isLoading ? '验证中...' : '验证解锁' }}
            </CommonButton>
          </div>
          <div class="form-text mt-2"><i class="bi bi-info-circle me-1"></i> 您需要先通过身份验证才能修改邮箱或密码。</div>
        </div>
      </div>

      <div v-else class="edit-zone animate__animated animate__fadeIn">

        <transition name="fade-slide">
          <div v-if="showUpdateHint" class="alert alert-success d-flex align-items-center mb-4 border-0 shadow-sm custom-alert">
            <i class="bi bi-check-circle-fill me-2"></i>
            <div>身份已验证，您现在可以修改以下信息</div>
            
            <button type="button" class="btn-close ms-auto" @click="showUpdateHint = false"></button>
          </div>
        </transition>

        <div class="mb-4">
          <label for="profile-change-email" class="form-label fw-bold text-secondary small">邮箱地址</label>
          <div class="input-group shadow-sm">
            <span class="input-group-text bg-white"><i class="bi bi-envelope"></i></span>
            <input id="profile-change-email" v-model="formData.email" type="email" class="form-control border-start-0" placeholder="请输入新邮箱" />
          </div>
          <div class="form-text mt-1 small">用于找回密码和接收通知</div>
        </div>
      
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <label for="profile-new-password" class="form-label fw-bold text-secondary small">新密码</label>
            <div class="input-group shadow-sm">
              <span class="input-group-text bg-white"><i class="bi bi-key"></i></span>
              <input id="profile-new-password" v-model="formData.newPassword" type="password" class="form-control border-start-0" placeholder="若不修改请留空" />
            </div>
            <div class="d-flex justify-content-between mt-1">
              <small class="form-text text-muted">长度至少 8 个字符</small>
              <div v-if="formData.newPassword.length > 0 && formData.newPassword.length < 8" class="text-danger small fw-bold">
                <i class="bi bi-exclamation-circle me-1"></i>长度不足
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <label for="profile-confirm-new-password" class="form-label fw-bold text-secondary small">确认新密码</label>
            <div class="input-group shadow-sm">
              <span class="input-group-text bg-white"><i class="bi bi-check-all"></i></span>
              <input id="profile-confirm-new-password" v-model="formData.confirmPassword" type="password" class="form-control border-start-0" placeholder="再次输入新密码" />
            </div>
          </div>
        </div>

        <div class="d-grid gap-2 mt-1">
          <CommonButton 
            native-type="submit" 
            theme="success" 
            size="md" 
            class="shadow rounded-pill w-100" 
            :disabled="isLoading"
          >
            <i class="bi bi-cloud-arrow-up me-2"></i>{{ isLoading ? '正在保存...' : '保存所有修改' }}
          </CommonButton>
          <button type="button" class="btn btn-link btn-sm text-secondary mt-2"
            @click="cancelEdit">取消修改
          </button>
        </div>
      </div>

    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, onUnmounted, defineEmits } from 'vue'
import { useAuth } from '../composables/useAuth'
import CommonButton from './CommonButton.vue'
import '../styles/components/labels.css'

const emit = defineEmits(['close'])

let errorTimer = null;
let noticeTimer = null;

const { user, updateProfile } = useAuth()

const formData = ref({
  email: '',
  password: '',
  newPassword: '',
  confirmPassword: ''
})

const message = ref('')
const messageType = ref('')
const isLoading = ref(false)
const isVerified = ref(false)
const showUpdateHint = ref(false)
const actionNotice = ref('')
const noticeType = ref('')

const formattedDate = computed(() => {
  if (user.value && user.value.created_at) {
    const dateString = user.value.created_at
    const utcString = dateString.endsWith('Z') ? dateString : dateString + 'Z'
    const date = new Date(utcString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }
  return '正在读取...'
})

const userTypeLabel = computed(() => {
  if (!user.value) return '加载中...'
  return user.value.is_admin ? '管理员' : '普通用户'
})

const showNotice = (text, type = 'info') => {
  if (noticeTimer) clearTimeout(noticeTimer)
  actionNotice.value = text
  noticeType.value = type

  noticeTimer = setTimeout(() => {
    actionNotice.value = '';
    noticeType.value = '';
    noticeTimer = null;
  }, 3000)
}

const clearMessage = () => {
  message.value = ''
  messageType.value = ''
}

const cancelEdit = () => {
  isVerified.value = false;
  formData.value.password = ''
  formData.value.newPassword = ''
  formData.value.confirmPassword = ''
  clearMessage()
  showNotice('已取消修改')
}

const showError = (text, type = 'danger') => {
  clearMessage()
  if (errorTimer) clearTimeout(errorTimer);
  message.value = '';
  nextTick(() => {
    message.value = text
    messageType.value = type

    errorTimer = setTimeout(() => {
      message.value = '';
    }, 3000)
  })
}

const verifyCurrentPassword = async () => {
  clearMessage()
  if (!formData.value.password) {
    showError('请输入当前密码进行验证', 'warning')
    return
  }

  isLoading.value = true
  clearMessage()
  try {
    await updateProfile(formData.value.email, formData.value.password, null, null)
    isVerified.value = true
    showUpdateHint.value = true
    showError('验证成功，请修改下方信息', 'success')
  } catch (error) {
    console.error('验证失败:', error)
    showError(error.response?.data?.message || '密码验证失败，请重试', 'danger')
    isVerified.value = false
  } finally {
    isLoading.value = false
  }
}
  
const handleUpdate = async () => {
  clearMessage()

  const { email, password, newPassword, confirmPassword } = formData.value;

  if (!password) {
    showError('请输入当前密码以进行验证', 'warning')
    return
  }

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (email === user.value.email && !newPassword) {
    showError('您没有修改任何信息', 'warning')
    return
  }

  if (!emailPattern.test(email)) {
    showError('请输入有效的邮箱地址', 'danger')
    return
  }

  if (newPassword) {
    if (newPassword.length > 0 && newPassword.length < 8) {
      showError('新密码长度至少需要 8 个字符', 'danger')
      return
    }

    if (password === newPassword) {
      showError('新密码不能与当前密码相同', 'danger')
      return
    }

    if (newPassword && newPassword !== confirmPassword) {
      showError('两次输入的密码不一致', 'danger')
      return
    }
  }

  isLoading.value = true
  try {
    await updateProfile(email, password, newPassword, confirmPassword)
    cancelEdit()
    showNotice('已保存所有修改！', 'success')
  } catch (error) {
    console.log('捕获到的错误详情:', error)
    const serverMessage = error.response?.data?.message || error.message || '更新失败'
    showError(serverMessage, 'danger')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  if (user.value) {
    formData.value.email = user.value.email
  }
})

onUnmounted(() => {
  if (errorTimer) {
    clearTimeout(errorTimer)
    errorTimer = null
  }
  if (noticeTimer) {
    clearTimeout(noticeTimer)
    noticeTimer = null
  }

  message.value = ''
  actionNotice.value = ''
  messageType.value = ''
  noticeType.value = ''
  showUpdateHint.value = false
  isVerified.value = false
})
</script>
