<template>
  <div class="container mt-5 mb-5">
    <div class="row justify-content-center">
      <div class="col-md-7">
        <div class="card shadow">
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
                <small class="form-text text-muted">密码长度至少为8个字符，建议包含字母、数字和特殊字符</small>
                <div v-if="formData.password.length > 0 && formData.password.length < 8" class="text-danger small mt-1">
                  <i class="bi bi-exclamation-circle me-1"></i>密码长度至少为 8 个字符
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
                <label class="form-check-label" for="terms">我已阅读并同意<a href="#" data-bs-toggle="modal" data-bs-target="#termsModal">服务条款</a>和<a href="#" data-bs-toggle="modal" data-bs-target="#privacyModal">隐私政策</a></label>
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

<!-- 服务条款模态框 -->
<div class="modal fade" id="termsModal" tabindex="-1" aria-labelledby="termsModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-scrollable">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="termsModalLabel">服务条款</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <h6>1. 接受条款</h6>
                <p>欢迎使用垃圾分类识别系统。通过使用本系统，您同意遵守本服务条款。</p>
                
                <h6>2. 系统服务</h6>
                <p>本系统提供垃圾图像上传、分类检测和结果展示等服务，旨在帮助用户正确分类垃圾。</p>
                
                <h6>3. 用户责任</h6>
                <p>用户应确保上传的图像不包含违法、侵权或不适当内容，否则系统有权删除相关内容并终止服务。</p>
                
                <h6>4. 知识产权</h6>
                <p>用户上传的图像版权归用户所有，但系统可以匿名使用这些数据进行模型训练和系统改进。</p>
                
                <h6>5. 免责声明</h6>
                <p>系统提供的分类结果仅供参考，不对因使用系统引起的任何直接或间接损失负责。</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
            </div>
        </div>
    </div>
</div>

<!-- 隐私政策模态框 -->
<div class="modal fade" id="privacyModal" tabindex="-1" aria-labelledby="privacyModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-scrollable">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="privacyModalLabel">隐私政策</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <h6>1. 收集的信息</h6>
                <p>我们收集用户在注册和使用过程中提供的信息，包括用户名、电子邮箱和上传的图像。</p>
                
                <h6>2. 信息使用</h6>
                <p>收集的信息用于提供服务、改进系统性能和用户体验。用户上传的图像可能被用于训练AI模型，但不会包含个人身份信息。</p>
                
                <h6>3. 信息保护</h6>
                <p>我们采用加密技术保护用户密码和敏感信息。未经用户同意，不会向第三方披露用户个人数据。</p>
                
                <h6>4. Cookie使用</h6>
                <p>系统使用Cookie记住用户登录状态和偏好设置，用户可以通过浏览器设置控制Cookie。</p>
                
                <h6>5. 隐私政策更新</h6>
                <p>我们保留修改隐私政策的权利，更新后将在网站公示，用户继续使用系统视为接受更新后的政策。</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
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
