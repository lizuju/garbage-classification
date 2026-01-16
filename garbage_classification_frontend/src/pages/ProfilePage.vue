<template>
  <div v-if="!isLoggedIn" class="container mt-5">
    <div class="alert alert-warning">请先<router-link to="/login">登录</router-link></div>
  </div>

  <div v-else class="container mt-5 mb-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-body">
            <h4 class="card-title">个人资料</h4>

            <div v-if="message" :class="`alert alert-${messageType}`">
              {{ message }}
            </div>

            <form @submit.prevent="handleUpdate">
              <div class="mb-3">
                <label class="form-label">用户名</label>
                <input v-model="user.username" type="text" class="form-control" disabled />
              </div>

              <div class="mb-3">
                <label class="form-label">邮箱</label>
                <input v-model="formData.email" type="email" class="form-control" />
              </div>

              <div class="mb-3">
                <label class="form-label">当前密码</label>
                <input v-model="formData.password" type="password" class="form-control" />
              </div>

              <div class="mb-3">
                <label class="form-label">新密码（不修改留空）</label>
                <input v-model="formData.newPassword" type="password" class="form-control" />
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
import { ref, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'

const { user, isLoggedIn, updateProfile } = useAuth()

const formData = ref({
  email: '',
  password: '',
  newPassword: '',
})

const message = ref('')
const messageType = ref('')
const isLoading = ref(false)

const handleUpdate = async () => {
  if (!formData.value.password) {
    message.value = '请输入当前密码以进行验证'
    messageType.value = 'warning'
    return
  }

  isLoading.value = true
  try {
    await updateProfile(formData.value.email, formData.value.password, formData.value.newPassword)
    message.value = '个人资料已更新'
    messageType.value = 'success'
    formData.value.password = ''
    formData.value.newPassword = ''
  } catch (error) {
    message.value = error.message || '更新失败'
    messageType.value = 'danger'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
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
