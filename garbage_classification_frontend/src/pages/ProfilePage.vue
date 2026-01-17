<template>
  <div v-if="!isLoggedIn" class="container mt-5">
    <div class="alert alert-warning">请先<router-link to="/login">登录</router-link></div>
  </div>

  <div v-else class="container mt-5 mb-5">
    <div class="row justify-content-center">
      <div class="col-md-7">
        <div class="card">
          <div class="card-body">
            <h3 class="card-title mb-2 text-center">个人资料</h3>
            <p class="text-muted mb-4 text-center">管理您的账户信息和设置</p>

            <div v-if="isLoading" class="text-center my-4">
              <div class="spinner-border text-success" role="status">
                <span class="visually-hidden">加载中...</span>
              </div>
              <p class="mt-2 text-muted">正在处理请求...</p>
            </div>

            <div v-if="message" :class="`alert alert-${messageType}`">
              {{ message }}
            </div>

            <form @submit.prevent="handleUpdate">
              <div class="mb-3">
                <label class="form-label">用户名</label>
                <input v-model="user.username" type="text" class="form-control" disabled />
              </div>

              <div class="mb-3">
                <label for="email" class="form-label">邮箱</label>
                <input id="email" v-model="formData.email" type="email" class="form-control" />
              </div>

              <div class="row mb-3 align-items-center">
                <div class="col-sm-3">
                  <strong>注册时间：</strong>
                </div>
                <div class="col-sm-9">
                  <span class="text-muted">{{ formattedDate }}</span>
                </div>
              </div>

              <div class="row">
                  <div class="col-sm-3"><strong>账户类型：</strong></div>
                  <div class="col-sm-9">
                      <span :class="userTypeBadgeClass">
                          {{ userTypeLabel }}
                      </span>
                  </div>
              </div>

              <div class="mb-3">
                <label for="current-password" class="form-label">当前密码</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-lock"></i></span>
                  <input id="current-password" v-model="formData.password" type="password" class="form-control" />
                </div>
              </div>

              <div class="mb-3">
                <label for="new-password" class="form-label">新密码</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-lock-fill"></i></span>
                  <input id="new-password" v-model="formData.newPassword" type="password" class="form-control" />
                </div>
                <small class="form-text text-muted">密码长度至少为8个字符</small>
                <div v-if="formData.newPassword.length > 0 && formData.newPassword.length < 8" class="text-danger small mt-1">
                  <i class="bi bi-exclamation-circle me-1"></i>密码长度至少为 8 个字符
                </div>
              </div>

              <div class="mb-3">
                <label for="confirm-new-password" class="form-label">确认新密码</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-lock-fill"></i></span>
                  <input id="confirm-new-password" v-model="formData.confirmPassword" type="password" class="form-control" />
                </div>
              </div>

              <button type="submit" class="btn btn-success" :disabled="isLoading">
                {{ isLoading ? '保存中...' : '保存修改' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
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

const handleUpdate = async () => {
  // 1. 验证当前密码
  if (!formData.value.password) {
    message.value = '请输入当前密码以进行验证'
    messageType.value = 'warning'
    return
  }

  // 2. 验证新密码长度（如果用户输入了新密码）
  if (formData.value.newPassword.length > 0 && formData.value.newPassword.length < 8) {
    message.value = '新密码长度至少需要 8 个字符'
    messageType.value = 'danger'
    return
  }

  // 3. 验证两次密码是否一致
  if (formData.value.newPassword !== formData.value.confirmPassword) {
    message.value = '两次输入的密码不一致'
    messageType.value = 'danger'
    return
  }

  isLoading.value = true
  try {
    await updateProfile(formData.value.email, formData.value.password, formData.value.newPassword, formData.value.confirmPassword)
    message.value = '个人资料已更新'
    messageType.value = 'success'
    formData.value.password = ''
    formData.value.newPassword = ''
    formData.value.confirmPassword = ''
  } catch (error) {
    console.log('捕获到的错误详情:', error);
    message.value = error.message || '更新失败'
    messageType.value = 'danger'
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
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-control:focus {
  border-color: #28a745;
  box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
}

.btn-success {
  background-color: #28a745;
}

.btn-success:hover {
  background-color: #218838;
}
</style>
