<template>
  <div class="card-body p-4 p-md-5">
    <div class="text-center mb-4">
      <h3 class="card-title fw-bold">{{ profileUser?.username }} 的账户信息</h3>
      <p class="text-muted">查看并管理{{ profileUser?.username }}的账户信息和安全设置</p>
    </div>

    <form @submit.prevent="handleUpdate" class="mt-4">
      <div class="mb-3 p-3 bg-light rounded-3 mx-0">
        <label class="form-label fw-bold text-secondary small">用户名</label>
        <div class="input-group">
          <span class="input-group-text bg-light border-0"><i class="bi bi-person text-muted"></i></span>
          <input :value="profileUser?.username" type="text" class="form-control bg-light border-0" disabled />
        </div>
      </div>

      <div class="mb-3 p-3 bg-light rounded-3 mx-0">
        <label for="profile-email" class="form-label fw-bold text-secondary small">邮箱地址</label>
        <div class="input-group">
          <span class="input-group-text bg-light border-0"><i class="bi bi-envelope text-muted"></i></span>
          <input id="profile-email" :value="profileUser?.email" type="email" class="form-control border-0 bg-light" disabled />
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
              <span :class="['role-label', profileUser?.is_admin ? 'admin' : 'user']">
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

      <div class="edit-zone animate__animated animate__fadeIn">
        <div class="mb-4">
          <label for="profile-change-username" class="form-label fw-bold text-secondary small">用户名</label>
          <div class="input-group shadow-sm">
            <span class="input-group-text bg-white"><i class="bi bi-person"></i></span>
            <input id="profile-change-username" v-model.trim="formData.username" type="text" class="form-control border-start-0" placeholder="请输入新用户名" />
          </div>
          <div class="form-text mt-1 small">用于用户登录，建议 3-20 个字符</div>
        </div>

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

      <div class="row g-3 mb-4">
        <div class="col-md-6">
          <label class="form-label fw-bold text-secondary small">用户角色</label>
          <select v-model="formData.is_admin" class="form-select" :disabled="isSelfUser">
            <option :value="true">管理员</option>
            <option :value="false">普通用户</option>
          </select>
          <div v-if="!isSelfUser && profileUser?.is_admin && formData.is_admin === false" class="form-text mt-1 small text-muted">
            若该用户是最后一个管理员，将无法降级
          </div>
          <div v-if="isSelfUser" class="form-text mt-1 small text-muted">
            不能降级当前登录管理员
          </div>
        </div>
        <div class="col-md-6">
          <label class="form-label fw-bold text-secondary small">账号状态</label>
          <select v-model="formData.is_active" class="form-select" :disabled="isAdminUser">
            <option :value="true">正常</option>
            <option :value="false">禁用</option>
          </select>
          <div v-if="isAdminUser" class="form-text mt-1 small text-muted">
            管理员账号状态不可更改
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
          <button type="button" class="btn btn-link btn-sm text-secondary mt-2" @click="emit('close')">
            取消修改
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onUnmounted, watch } from 'vue'
import { useApi } from '../composables/useApi'
import { useAuth } from '../composables/useAuth'
import CommonButton from './CommonButton.vue'
import '../styles/components/labels.css'

const props = defineProps({
  user: { type: Object, default: null }
})

const emit = defineEmits(['close', 'updated'])

let errorTimer = null
let noticeTimer = null

const { updateAdminUser } = useApi()
const { user: currentUser } = useAuth()

const formData = ref({
  username: '',
  email: '',
  newPassword: '',
  confirmPassword: '',
  is_admin: false,
  is_active: true
})

const message = ref('')
const messageType = ref('')
const isLoading = ref(false)
const actionNotice = ref('')
const noticeType = ref('')

const profileUser = computed(() => props.user)
const isSelfUser = computed(() => !!currentUser.value && !!profileUser.value && currentUser.value.id === profileUser.value.id)
const isAdminUser = computed(() => !!formData.value.is_admin)

const formattedDate = computed(() => {
  if (profileUser.value && profileUser.value.created_at) {
    const dateString = profileUser.value.created_at
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
  if (!profileUser.value) return '加载中...'
  return profileUser.value.is_admin ? '管理员' : '普通用户'
})

const showNotice = (text, type = 'info') => {
  if (noticeTimer) clearTimeout(noticeTimer)
  actionNotice.value = text
  noticeType.value = type

  noticeTimer = setTimeout(() => {
    actionNotice.value = ''
    noticeType.value = ''
    noticeTimer = null
  }, 3000)
}

const clearMessage = () => {
  message.value = ''
  messageType.value = ''
}

const showError = (text, type = 'danger') => {
  clearMessage()
  if (errorTimer) clearTimeout(errorTimer)
  message.value = ''
  nextTick(() => {
    message.value = text
    messageType.value = type

    errorTimer = setTimeout(() => {
      message.value = ''
    }, 3000)
  })
}

const handleUpdate = async () => {
  clearMessage()
  if (!profileUser.value) return

  const { username, email, newPassword, confirmPassword } = formData.value
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  const currentUsername = profileUser.value?.username || ''
  const currentEmail = profileUser.value?.email || ''
  const currentIsAdmin = !!profileUser.value?.is_admin
  const currentIsActive = profileUser.value?.is_active !== false

  const hasChanges = (
    username !== currentUsername ||
    email !== currentEmail ||
    !!newPassword ||
    formData.value.is_admin !== currentIsAdmin ||
    formData.value.is_active !== currentIsActive
  )

  if (!hasChanges) {
    showError('您没有修改任何信息', 'warning')
    return
  }

  if (isSelfUser.value && formData.value.is_admin === false) {
    showError('不能降级当前登录管理员', 'danger')
    return
  }

  if (!username || username.length < 3 || username.length > 20) {
    showError('用户名长度需为 3-20 个字符', 'danger')
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

    if (newPassword && newPassword !== confirmPassword) {
      showError('两次输入的密码不一致', 'danger')
      return
    }
  }

  isLoading.value = true
  try {
    const payload = {
      username,
      email,
      is_admin: formData.value.is_admin,
      is_active: formData.value.is_active
    }
    if (profileUser.value?.is_admin) {
      payload.is_active = true
    }
    if (newPassword) {
      payload.new_password = newPassword
      payload.confirm_password = confirmPassword
    }
    const result = await updateAdminUser(profileUser.value.id, payload)
    if (result.user) {
      emit('updated', result.user)
    }
    showNotice('已保存所有修改！', 'success')
    emit('close')
  } catch (error) {
    const serverMessage = error.response?.data?.message || error.message || '更新失败'
    showError(serverMessage, 'danger')
  } finally {
    isLoading.value = false
  }
}

watch(
  () => props.user,
  (nextUser) => {
    if (nextUser) {
      formData.value.username = nextUser.username || ''
      formData.value.email = nextUser.email || ''
      formData.value.newPassword = ''
      formData.value.confirmPassword = ''
      formData.value.is_admin = !!nextUser.is_admin
      formData.value.is_active = nextUser.is_active !== false
    }
  },
  { immediate: true }
)

watch(
  () => formData.value.is_admin,
  (isAdmin) => {
    if (isAdmin) {
      formData.value.is_active = true
    }
  }
)

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
})
</script>
