<template>
  <teleport to="body">
    <transition name="fade">
      <div v-if="isOpen" class="modal-backdrop-blur" @click.self="handleClose">
        <transition name="zoom-fade">
          <div v-reveal class="modal-container card card-glass hero-fade-in">
            <CommonButton 
              theme="glass-dark" 
              circle 
              size="md" 
              class="modal-close-btn" 
              @click="handleClose" 
              aria-label="关闭"
            >
              <i class="bi bi-x-lg"></i>
            </CommonButton>

            <div class="modal-content-inner">
              <div class="bg-success" style="height: 6px; border-radius: 24px 24px 0 0;"></div>
              <div class="card-body p-4 p-md-5 no-text-shadow">
                <h3 class="card-title fw-bold text-center mb-3">{{ title }}</h3>
                <div class="text-muted">
                  <template v-if="type === 'terms'">
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
                  </template>
                  <template v-else>
                    <h6>1. 信息收集</h6>
                    <p>我们仅收集提供服务所必需的信息，如用户名、邮箱等。</p>
                    
                    <h6>2. 信息使用</h6>
                    <p>收集的信息用于账户认证、服务优化以及必要的通知。</p>
                    
                    <h6>3. 信息保护</h6>
                    <p>我们采取合理措施保护您的信息安全，防止未经授权的访问与泄露。</p>
                    
                    <h6>4. 信息共享</h6>
                    <p>未经用户同意，不会向第三方分享用户隐私信息，法律法规要求除外。</p>
                    
                    <h6>5. 隐私政策更新</h6>
                    <p>我们保留修改隐私政策的权利，更新后将在网站公示，用户继续使用系统视为接受更新后的政策。</p>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { computed } from 'vue'
import CommonButton from './CommonButton.vue'
import '../styles/components/modal.css'
import '../styles/components/card.css'
import '../styles/components/common-button.css'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  type: { type: String, default: 'terms' } // 'terms' | 'privacy'
})

const emit = defineEmits(['close'])

const title = computed(() => (props.type === 'terms' ? '服务条款' : '隐私政策'))

const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
.no-text-shadow,
.no-text-shadow * {
  text-shadow: none !important;
}
</style>
