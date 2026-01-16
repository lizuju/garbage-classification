<template>
  <div v-if="!isLoggedIn" class="container mt-5">
    <div class="alert alert-warning">请先<router-link to="/login">登录</router-link>以使用识别功能</div>
  </div>

  <div v-else>
    <!-- 页面头部 - 整合旧 HTML 样式 -->
    <div class="page-header">
      <div class="container">
        <h1>垃圾识别</h1>
        <p class="lead">上传一张包含垃圾的图片，AI 将自动检测并识别垃圾类别</p>
      </div>
    </div>

    <div class="container mb-5">
      <div class="alert alert-info">
        <i class="bi bi-info-circle-fill me-2"></i>
        支持 JPG、JPEG、PNG 格式的图片，最大 5MB。图片质量越清晰，识别效果越好。<strong>系统使用低置信度阈值(0.1)，可更好地识别垃圾物品。</strong>
      </div>

      <div v-if="message" :class="`alert alert-${messageType}`" role="alert">
        {{ message }}
      </div>

      <div class="row">
        <!-- 左侧：上传区域 -->
        <div class="col-lg-6">
          <div class="card mb-4">
            <div class="card-body">
              <h5 class="card-title">上传图片</h5>

              <!-- 上传区域 - 整合旧 HTML 样式 -->
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
                <img :src="preview" alt="preview" class="preview-image" />
                <button
                  type="button"
                  class="btn btn-danger btn-sm remove-btn"
                  @click="resetUpload"
                >
                  <i class="bi bi-x-lg"></i>
                </button>
              </div>

              <div class="d-grid gap-2 mt-3">
                <button
                  type="button"
                  class="btn btn-primary"
                  :disabled="!selectedFile || isLoading"
                  @click="handleDetect"
                >
                  <i class="bi bi-search me-1"></i>
                  {{ isLoading ? '识别中...' : '开始识别' }}
                </button>
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
                <div v-if="results.result_url" class="mb-3">
                  <img :src="results.result_url" :alt="results.result_url" class="img-fluid rounded" />
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useApi } from '../composables/useApi'

const { isLoggedIn } = useAuth()
const { detect } = useApi()

const fileInput = ref(null)
const selectedFile = ref(null)
const preview = ref(null)
const results = ref(null)
const isLoading = ref(false)
const isDragOver = ref(false)
const message = ref('')
const messageType = ref('')

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

<style scoped>
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px 0;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.page-header .lead {
  font-size: 1.2rem;
  opacity: 0.9;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f8f9fa;
  min-height: 250px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #28a745;
  background-color: #f1f9f1;
  transform: scale(1.02);
}

.upload-area.drag-over {
  border-color: #28a745;
  background-color: #e8f5e9;
}

.upload-icon {
  font-size: 60px;
  color: #28a745;
  margin-bottom: 15px;
}

.preview-container {
  position: relative;
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.remove-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  border-radius: 50%;
  width: 40px;
  height: 40px;
}

.category-label {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 20px;
  color: white;
  font-weight: bold;
  margin-right: 8px;
  font-size: 0.875rem;
}

.category-label.recyclable {
  background-color: #28a745;
}

.category-label.harmful {
  background-color: #dc3545;
}

.category-label.kitchen {
  background-color: #fd7e14;
}

.category-label.other {
  background-color: #6c757d;
}

.loader {
  padding: 40px;
  text-align: center;
}

.result-container {
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
