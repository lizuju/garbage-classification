<template>
  <div class="detect-page-wrapper">
    <div v-if="!isLoggedIn" class="container mt-5">
      <div class="alert alert-warning">
        请先<router-link to="/login">登录</router-link>以使用识别功能
      </div>
    </div>

    <div v-else>
      <!-- 页面头部 -->
      <PageHero
        title="识别检测"
        subtitle="支持多种识别方式，AI 自动检测并分类垃圾"
        ctaText="开始识别"
        ctaLink="#garbage-identification"
      />

        <div class="detect-content">
          <h2 v-reveal id="garbage-identification" class="section-title hero-fade-in anim-delay-1">垃圾识别</h2>
          <!-- Content remains the same -->
          <div class="alert alert-info">
            <i class="bi bi-info-circle-fill me-2"></i>
            支持 JPG、JPEG、PNG 格式的图片，最大 5MB。图片质量越清晰，识别效果越好。<strong>系统使用低置信度阈值(0.1)，可更好地识别垃圾物品。</strong>
          </div>

          <div v-if="message" :class="`alert alert-${messageType}`" role="alert">
            {{ message }}
          </div>

          <!-- Mode Toggle Tabs -->
          <div class="mode-tabs mb-4 text-center">
              <div class="d-flex justify-content-center gap-3">
                  <common-button 
                    :theme="detectMode === 'upload' ? 'primary' : 'purple'"
                    size="md"
                    :disabled="detectMode === 'upload'"
                    @click="setMode('upload')"
                  >
                      <i class="bi bi-cloud-arrow-up me-2"></i>图片上传
                  </common-button>
                  <common-button 
                    :theme="detectMode === 'camera' ? 'primary' : 'purple'"
                    size="md"
                    :disabled="detectMode === 'camera'"
                    @click="setMode('camera')"
                  >
                      <i class="bi bi-camera-video me-2"></i>实时摄像头
                  </common-button>
              </div>
          </div>

          <div v-if="detectMode === 'camera'">
            <div class="card mb-4">
               <div class="card-body">
                  <h5 class="card-title text-center mb-4">实时摄像头识别</h5>
                  <camera-detect @error="handleCameraError" />
               </div>
            </div>
          </div>

          <div v-else class="row">
            <!-- 左侧：上传区域 -->
            <div class="col-lg-6">
              <div class="card mb-4">
                <div class="card-body">
                  <h5 class="card-title">上传图片</h5>

                  <!-- 上传区域 -->
                  <div
                    class="upload-area"
                    :class="{ 'drag-over': isDragOver }"
                    @click="triggerFileInput"
                    @dragover.prevent="isDragOver = true"
                    @dragleave="isDragOver = false"
                    @drop.prevent="handleDrop"
                  >
                    <i class="bi bi-cloud-arrow-up upload-icon"></i>
                    <h5>点击或拖拽图片到此处</h5>
                    <p class="text-muted">支持 JPG、JPEG、PNG 格式</p>
                  </div>

                  <input
                    ref="fileInput"
                    type="file"
                    class="d-none"
                    accept="image/*"
                    @change="handleFileSelect"
                  />

                  <!-- 预览图 -->
                  <div v-if="preview" class="preview-container">
                    <div class="image-wrapper"> <img :src="preview" alt="preview" class="preview-image" />
                      <button
                        type="button"
                        class="btn-danger remove-btn"
                        @click="resetUpload"
                      >
                        <i class="bi bi-x-lg"></i>
                      </button>
                    </div>
                  </div>

                  <div class="d-grid gap-2 mt-3">
                    <common-button
                      theme="primary"
                      size="md"
                      :disabled="!selectedFile || isLoading"
                      @click="handleDetect"
                    >
                      <i class="bi bi-search me-1"></i>
                      {{ isLoading ? '识别中...' : '开始识别' }}
                    </common-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 右侧：结果展示区 -->
            <div class="col-lg-6">
              <!-- 加载动画 -->
              <div v-if="isLoading" class="loader text-center">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">加载中...</span>
                </div>
                <p class="mt-2">正在分析图片，请稍候...</p>
              </div>

              <!-- 结果展示 -->
              <div v-if="results" class="result-container">
                <div class="card">
                  <div class="card-body">
                    <h5 class="card-title">识别结果</h5>

                    <!-- 结果图 -->
                    <div v-if="results.result_url_base64" class="mb-3">
                      <img :src="results.result_url_base64" alt="detection result" class="img-fluid rounded" />
                    </div>

                    <!-- 检测到的物品 -->
                    <div v-if="results.results && results.results.length > 0">
                      <div class="alert alert-success">
                        <h6><i class="bi bi-check-circle-fill me-2"></i> 检测到 {{ results.results.length }} 个物体</h6>
                      </div>

                      <div class="table-responsive">
                        <table class="table table-sm">
                          <thead>
                            <tr>
                              <th>物品名称</th>
                              <th>信心度</th>
                              <th>位置</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="(item, idx) in results.results" :key="idx">
                              <td>
                                <span :class="`category-label ${getCategoryClass(item.class_name)}`">
                                  {{ item.class_name }}
                                </span>
                              </td>
                              <td>
                                <div class="progress" style="height: 20px">
                                  <div
                                    class="progress-bar bg-success"
                                    :style="{ width: `${(item.confidence * 100).toFixed(1)}%` }"
                                  >
                                    {{ (item.confidence * 100).toFixed(1) }}%
                                  </div>
                                </div>
                              </td>
                              <td>
                                {{
                                  item.bbox
                                    ? `[${item.bbox[0].toFixed(0)}, ${item.bbox[1].toFixed(0)}]`
                                    : 'N/A'
                                }}
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                    <div v-else class="alert alert-info">
                      <i class="bi bi-info-circle me-2"></i>未检测到垃圾物品
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useApi } from '../composables/useApi'
import CommonButton from '@/components/CommonButton.vue'
import PageHero from '@/components/PageHero.vue'
import CameraDetect from '@/components/CameraDetect.vue'
import '../styles/pages/detect.css'

const { isLoggedIn } = useAuth()
const { detect } = useApi()

const detectMode = ref('upload') // 'upload' or 'camera'

const fileInput = ref(null)
const selectedFile = ref(null)
const preview = ref(null)
const results = ref(null)
const isLoading = ref(false)
const isDragOver = ref(false)
const message = ref('')
const messageType = ref('')

const setMode = (mode) => {
  detectMode.value = mode
  message.value = ''
}

const handleCameraError = (err) => {
  message.value = '摄像头启动失败: ' + err.message
  messageType.value = 'danger'
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (e) => {
  const file = e.target.files?.[0]
  if (file && file.type.startsWith('image/')) {
    selectedFile.value = file
    const reader = new FileReader()
    reader.onload = (evt) => {
      preview.value = evt.target?.result
    }
    reader.readAsDataURL(file)
    message.value = ''
  } else {
    message.value = '请选择有效的图片文件'
    messageType.value = 'warning'
  }
}

const handleDrop = (e) => {
  isDragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) {
    selectedFile.value = file
    const reader = new FileReader()
    reader.onload = (evt) => {
      preview.value = evt.target?.result
    }
    reader.readAsDataURL(file)
    message.value = ''
  }
}

const handleDetect = async () => {
  if (!selectedFile.value) {
    message.value = '请先选择图片'
    messageType.value = 'warning'
    return
  }

  isLoading.value = true
  try {
    const result = await detect(selectedFile.value)
    results.value = result
    message.value = '识别完成！'
    messageType.value = 'success'
  } catch (error) {
    message.value = error.message || '识别失败，请重试'
    messageType.value = 'danger'
  } finally {
    isLoading.value = false
  }
}

const resetUpload = () => {
  selectedFile.value = null
  preview.value = null
  results.value = null
  message.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const getCategoryClass = (className) => {
  const classMap = {
    '可回收': 'recyclable',
    '有害': 'harmful',
    '厨余': 'kitchen',
    '其他': 'other',
  }
  return classMap[className] || 'other'
}
</script>