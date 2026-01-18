<template>
  <div v-if="!isLoggedIn" class="container mt-5">
    <div class="alert alert-warning shadow-sm">
      <i class="bi bi-exclamation-triangle me-2"></i>请先<router-link to="/login" class="alert-link">登录</router-link>
    </div>
  </div>

  <div v-else class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-7">
        <div class="card border-0 shadow-lg rounded-4 overflow-hidden">
          <div class="bg-success" style="height: 6px;"></div>
          
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
                  <input v-model="user.username" type="text" class="form-control bg-light border-0" disabled />
                </div>
              </div>

              <div class="mb-3 p-3 bg-light rounded-3 mx-0">
                <label for="email" class="form-label fw-bold text-secondary small">邮箱地址</label>
                <div class="input-group">
                  <span class="input-group-text bg-light border-0"><i class="bi bi-envelope text-muted"></i></span>
                  <input id="email" v-model="formData.email" type="email" class="form-control border-0 bg-light" disabled />
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
                      <span :class="userTypeBadgeClass + ' px-3 py-1 rounded-pill'" style="font-size: 0.85rem;">
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
                  <label for="current-password" class="form-label fw-bold text-secondary small">
                    第一步：请输入当前密码验证身份 <span class="text-danger">*</span>
                  </label>
                  <div class="input-group">
                    <span class="input-group-text bg-white"><i class="bi bi-lock"></i></span>
                    <input 
                      id="current-password" 
                      v-model="formData.password" 
                      type="password" 
                      class="form-control border-start-0" 
                      placeholder="输入当前密码以解锁编辑"
                      @keyup.enter="verifyCurrentPassword"
                    />
                    <button class="btn btn-success px-4" type="button" @click="verifyCurrentPassword" :disabled="isLoading">
                      {{ isLoading ? '验证中...' : '验证解锁' }}
                    </button>
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
                  <label for="change-email" class="form-label fw-bold text-secondary small">邮箱地址</label>
                  <div class="input-group shadow-sm">
                    <span class="input-group-text bg-white"><i class="bi bi-envelope"></i></span>
                    <input id="change-email" v-model="formData.email" type="email" class="form-control border-start-0" placeholder="请输入新邮箱" />
                  </div>
                  <div class="form-text mt-1 small">用于找回密码和接收通知</div>
                </div>
              
                <div class="row g-3 mb-4">
                  <div class="col-md-6">
                    <label for="new-password" class="form-label fw-bold text-secondary small">新密码</label>
                    <div class="input-group shadow-sm">
                      <span class="input-group-text bg-white"><i class="bi bi-key"></i></span>
                      <input id="new-password" v-model="formData.newPassword" type="password" class="form-control border-start-0" placeholder="若不修改请留空" />
                    </div>
                    <div class="d-flex justify-content-between mt-1">
                      <small class="form-text text-muted">长度至少 8 个字符</small>
                      <div v-if="formData.newPassword.length > 0 && formData.newPassword.length < 8" class="text-danger small fw-bold">
                        <i class="bi bi-exclamation-circle me-1"></i>长度不足
                      </div>
                    </div>
                  </div>

                  <div class="col-md-6">
                    <label for="confirm-new-password" class="form-label fw-bold text-secondary small">确认新密码</label>
                    <div class="input-group shadow-sm">
                      <span class="input-group-text bg-white"><i class="bi bi-check-all"></i></span>
                      <input id="confirm-new-password" v-model="formData.confirmPassword" type="password" class="form-control border-start-0" placeholder="再次输入新密码" />
                    </div>
                  </div>
                </div>

                <div class="d-grid gap-2 mt-5">
                  <button type="submit" class="btn btn-success btn-lg shadow rounded-pill" :disabled="isLoading">
                    <i class="bi bi-cloud-arrow-up me-2"></i>{{ isLoading ? '正在保存...' : '保存所有修改' }}
                  </button>
                  <button type="button" class="btn btn-link btn-sm text-secondary mt-2"
                    @click="cancelEdit">取消修改
                  </button>
                </div>
              </div>

            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useAuth } from '../composables/useAuth'

const { user, isLoggedIn, updateProfile } = useAuth()

const formData = ref({
  email: '',
  password: '',
  newPassword: '',
  confirmPassword: ''
})

const message = ref('')
const messageType = ref('')
const isLoading = ref(false)
const isVerified = ref(false) // 控制是否显示修改表单
const showUpdateHint = ref(false);  // 交互辅助：仅控制绿色提示条的显示
const actionNotice = ref('') // 专门用于存储“修改成功”或“取消修改”的文字
const noticeType = ref('')

const formattedDate = computed(() => {
  if (user.value && user.value.created_at) {
    const date = new Date(user.value.created_at)
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

// 1. 计算显示的文字
const userTypeLabel = computed(() => {
  if (!user.value) return '加载中...'
  return user.value.is_admin ? '管理员' : '普通用户'
})

// 2. 计算 Badge 的颜色类名
const userTypeBadgeClass = computed(() => {
  const baseClass = 'badge '
  if (!user.value) return baseClass + 'bg-secondary'
  
  // 管理员显示红色 (bg-danger)，普通用户显示灰色 (bg-secondary)
  return user.value.is_admin ? baseClass + 'bg-danger' : baseClass + 'bg-secondary'
})

const showNotice = (text, type = 'info') => {
  actionNotice.value = text
  noticeType.value = type
  
  // 3秒后自动清空
  setTimeout(() => {
    actionNotice.value = ''
    noticeType.value = ''
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

// 定义一个专业的报错辅助函数
const showError = (text, type = 'danger') => {
  clearMessage()
  nextTick(() => {
    message.value = text
    messageType.value = type
  })
}

// 第一步：验证当前密码
const verifyCurrentPassword = async () => {
  clearMessage()
  if (!formData.value.password) {
    showError('请输入当前密码进行验证', 'warning')
    return
  }

  isLoading.value = true
  clearMessage()
  try {
    await updateProfile(formData.value.email, formData.value.password, null, null) // 复用更新接口进行验证
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
  // 1. 验证当前密码
  if (!formData.value.password) {
    showError('请输入当前密码以进行验证', 'warning')
    return
  }

  // 1.只有当用户输入了新密码时才进行此检查
  if (formData.value.newPassword) {
    // 2. 验证新密码长度
    if (formData.value.newPassword.length > 0 && formData.value.newPassword.length < 8) {
      showError('新密码长度至少需要 8 个字符', 'danger')
      return
    }

    // 3. 检查新旧密码是否相同
    if (formData.value.password === formData.value.newPassword) {
      showError('新密码不能与当前密码相同', 'danger')
      return
    }

    // 4. 验证两次密码是否一致
    if (formData.value.newPassword && formData.value.newPassword !== formData.value.confirmPassword) {
      showError('两次输入的密码不一致', 'danger')
      return
    }
  }

  isLoading.value = true
  try {
    await updateProfile(formData.value.email, formData.value.password, formData.value.newPassword, formData.value.confirmPassword)
    showError('个人资料已更新', 'success')
    cancelEdit()
    showNotice('已保存所有修改！')
  } catch (error) {
    console.log('捕获到的错误详情:', error);
    showError(error.message || '更新失败', 'danger')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  console.log('【ProfilePage】用户信息:', user.value);

  if (user.value) {
    formData.value.email = user.value.email
  }
})
</script>

<style scoped>
.card {
  transition: all 0.3s ease;
}

/* 输入框聚焦效果 */
.form-control:focus {
  border-color: #28a745;
  box-shadow: 0 0 0 0.25rem rgba(40, 167, 69, 0.1);
  background-color: #fff !important;
}

.input-group-text {
  border: 1px solid #ced4da;
}

.form-control {
  border: 1px solid #ced4da;
}

/* 按钮悬停效果 */
.btn-success {
  background-color: #28a745;
  border: none;
  font-weight: 600;
  padding: 12px;
}

.btn-success:hover {
  background-color: #218838;
  transform: translateY(-1px);
}

.btn-success:disabled {
  background-color: #6c757d;
}

/* 提示框淡出动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
  margin-bottom: -58px; /* 消失时自动收缩空间，不留白 */
}

.custom-alert {
  z-index: 10;
  position: relative;
}

/* 专属弹窗动画：弹跳感更强 */
.zoom-fade-enter-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.zoom-fade-leave-active {
  transition: all 0.3s ease;
}
.zoom-fade-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(-10px);
}
.zoom-fade-leave-to {
  opacity: 0;
  transform: scale(1.1); /* 消失时轻微变大，给人“炸开”消失的感觉 */
}

.alert {
  backdrop-filter: blur(4px); /* 背景模糊，看起来更有高级质感 */
  font-weight: 500;
}
</style>
