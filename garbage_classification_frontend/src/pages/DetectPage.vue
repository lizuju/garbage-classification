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
            支持 JPG、JPEG、PNG 格式的图片，可单张或批量上传（最多 20 张，单张不超过 5MB，总大小不超过 30MB）。图片质量越清晰，识别效果越好。<strong>系统使用低置信度阈值(0.1)，可更好地识别垃圾物品。</strong>
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
                      <i class="bi bi-camera-video me-2"></i>实时检测
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
                    <h5>点击或拖拽图片到此处（支持批量）</h5>
                    <p class="text-muted">支持 JPG、JPEG、PNG 格式，最多 20 张</p>
                  </div>

                  <input
                    ref="fileInput"
                    type="file"
                    class="d-none"
                    accept="image/*"
                    multiple
                    @change="handleFileSelect"
                  />

                  <!-- 预览图 -->
                  <div v-if="previews.length > 0" class="preview-container">
                    <div class="preview-grid">
                      <div v-for="(item, index) in previews" :key="`${item.name}-${index}`" class="image-wrapper">
                        <div class="image-frame">
                          <img :src="item.url" alt="preview" class="preview-image" />
                          <CommonButton
                            theme="danger"
                            circle
                            size="xs"
                            class="remove-btn"
                            @click.stop="removeSelectedFile(index)"
                            type="button"
                          >
                            <i class="bi bi-x-lg"></i>
                          </CommonButton>
                        </div>
                        <div class="preview-name text-truncate">{{ item.name }}</div>
                      </div>
                    </div>
                  </div>
                  <div v-if="selectedFiles.length > 0" class="selected-count">
                    已选择 {{ selectedFiles.length }} 张图片
                  </div>
                  <div v-if="selectedFiles.length > 0" class="d-grid gap-2 mt-2">
                    <CommonButton
                      theme="danger"
                      size="sm"
                      @click="resetUpload"
                      type="button"
                    >
                      <i class="bi bi-x-lg me-1"></i>清空已选图片
                    </CommonButton>
                  </div>

                  <div class="d-grid gap-2 mt-3">
                    <common-button
                      theme="success"
                      size="md"
                      :disabled="selectedFiles.length === 0 || isLoading"
                      @click="handleDetect"
                    >
                      <i class="bi bi-search me-1"></i>
                      {{ isLoading ? '识别中...' : selectedFiles.length > 1 ? `开始批量识别（${selectedFiles.length} 张）` : '开始识别' }}
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
              <div v-if="detectionResults.length > 0" class="result-container">
                <div class="card mb-3" v-for="(result, resIndex) in detectionResults" :key="`${result.image_id || 'err'}-${resIndex}`">
                  <div class="card-body">
                    <h5 class="card-title">
                      识别结果 {{ detectionResults.length > 1 ? `#${resIndex + 1}` : '' }}
                    </h5>
                    <p class="small text-muted mb-2">{{ result.filename || '未命名文件' }}</p>

                    <div v-if="result.status !== 'success'" class="alert alert-danger mb-3">
                      <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ result.message || '识别失败' }}
                    </div>

                    <!-- 结果图 -->
                    <div v-if="result.status === 'success' && result.result_url_base64" class="mb-3">
                      <img :src="result.result_url_base64" alt="detection result" class="img-fluid rounded" />
                    </div>

                    <!-- 检测到的物品 -->
                    <div v-if="result.status === 'success' && result.results && result.results.length > 0">
                      <div class="alert alert-success">
                        <h6><i class="bi bi-check-circle-fill me-2"></i> 检测到 {{ result.results.length }} 个物体</h6>
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
                            <tr v-for="(item, idx) in result.results" :key="idx">
                              <td>
                                <span :class="`category-label ${getCategoryClass(item.class_name)}`">
                                  {{ item.class_name }}
                                </span>
                              </td>
                              <td>
                                <div v-if="item.confidence && item.confidence > 0" class="gc-progress-container">
                                  <div
                                    class="gc-progress-bar"
                                    :class="getProgressLevelClass(item.confidence)"
                                    :style="{ width: `${(item.confidence * 100).toFixed(1)}%` }"
                                  ></div>
                                  <span class="gc-progress-label">{{ (item.confidence * 100).toFixed(1) }}%</span>
                                </div>
                                <span v-else class="text-muted small">无法识别</span>
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
                    <div v-else-if="result.status === 'success'" class="alert alert-info">
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
import { ref, onUnmounted } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useApi } from '../composables/useApi'
import CommonButton from '@/components/CommonButton.vue'
import PageHero from '@/components/PageHero.vue'
import CameraDetect from '@/components/CameraDetect.vue'
import '../styles/pages/detect.css'
import '../styles/components/progress.css'
import '../styles/components/labels.css'

const { isLoggedIn } = useAuth()
const { detect, detectBatch } = useApi()

const detectMode = ref('upload') // 'upload' or 'camera'

const fileInput = ref(null)
const selectedFiles = ref([])
const previews = ref([])
const detectionResults = ref([])
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

const MAX_BATCH_FILES = 20
const MAX_SINGLE_FILE_SIZE = 5 * 1024 * 1024
const MAX_TOTAL_UPLOAD_SIZE = 30 * 1024 * 1024

const revokePreviewUrls = () => {
  previews.value.forEach((item) => {
    if (item?.url) URL.revokeObjectURL(item.url)
  })
}

const setSelectedFiles = (files) => {
  revokePreviewUrls()
  const imageFiles = files.filter((file) => file && file.type.startsWith('image/')).slice(0, MAX_BATCH_FILES)
  const oversized = imageFiles.find((file) => file.size > MAX_SINGLE_FILE_SIZE)
  if (oversized) {
    selectedFiles.value = []
    previews.value = []
    message.value = `文件 ${oversized.name} 超过 5MB，请压缩后再上传`
    messageType.value = 'warning'
    return
  }
  const totalSize = imageFiles.reduce((sum, file) => sum + (file.size || 0), 0)
  if (totalSize > MAX_TOTAL_UPLOAD_SIZE) {
    selectedFiles.value = []
    previews.value = []
    message.value = '批量上传总大小不能超过 30MB，请减少文件数量或压缩图片'
    messageType.value = 'warning'
    return
  }

  const validImages = imageFiles
  selectedFiles.value = validImages
  previews.value = validImages.map((file) => ({
    name: file.name,
    url: URL.createObjectURL(file),
  }))
}

const handleFileSelect = (e) => {
  const files = Array.from(e.target.files || [])
  if (files.length > 0 && files.some((file) => file.type.startsWith('image/'))) {
    setSelectedFiles(files)
    detectionResults.value = []
    message.value = ''
  } else {
    message.value = '请选择有效的图片文件'
    messageType.value = 'warning'
  }
}

const handleDrop = (e) => {
  isDragOver.value = false
  const files = Array.from(e.dataTransfer?.files || [])
  if (files.length > 0 && files.some((file) => file.type.startsWith('image/'))) {
    setSelectedFiles(files)
    detectionResults.value = []
    message.value = ''
  } else {
    message.value = '请选择有效的图片文件'
    messageType.value = 'warning'
  }
}

const handleDetect = async () => {
  if (selectedFiles.value.length === 0) {
    message.value = '请先选择图片'
    messageType.value = 'warning'
    return
  }

  isLoading.value = true
  try {
    if (selectedFiles.value.length === 1) {
      const result = await detect(selectedFiles.value[0])
      detectionResults.value = [result]
      message.value = '识别完成！'
    } else {
      const batchResult = await detectBatch(selectedFiles.value)
      detectionResults.value = batchResult.items || []
      message.value = batchResult.message || '批量识别完成！'
    }
    messageType.value = 'success'
  } catch (error) {
    message.value = error.message || '识别失败，请重试'
    messageType.value = 'danger'
  } finally {
    isLoading.value = false
  }
}

const resetUpload = () => {
  revokePreviewUrls()
  selectedFiles.value = []
  previews.value = []
  detectionResults.value = []
  message.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const removeSelectedFile = (index) => {
  const target = previews.value[index]
  if (target?.url) {
    URL.revokeObjectURL(target.url)
  }
  selectedFiles.value.splice(index, 1)
  previews.value.splice(index, 1)
  detectionResults.value = []

  if (selectedFiles.value.length === 0 && fileInput.value) {
    fileInput.value.value = ''
  }
}

const getProgressLevelClass = (confidence) => {
  if (confidence >= 0.9) return 'lvl-excellent'
  if (confidence >= 0.7) return 'lvl-high'
  if (confidence >= 0.4) return 'lvl-medium'
  return 'lvl-low'
}

const getCategoryClass = (className) => {
  const classMap = {
    '可回收垃圾': 'recyclable',
    '有害垃圾': 'harmful',
    '厨余垃圾': 'kitchen',
    '其他垃圾': 'other',
  }
  return classMap[className] || 'other'
}

onUnmounted(() => {
  revokePreviewUrls()
})
</script>
