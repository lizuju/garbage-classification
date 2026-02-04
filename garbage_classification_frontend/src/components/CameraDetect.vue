<template>
  <div class="camera-detect-container">
    <!-- Camera Viewport -->
    <div class="camera-viewport mb-3">
      <video ref="videoRef" class="camera-video" autoplay playsinline muted></video>
      <canvas ref="canvasRef" class="camera-canvas"></canvas>
      
      <!-- Loading Overlay -->
      <div v-if="isInitializing" class="camera-overlay">
        <div class="spinner-border text-light" role="status"></div>
        <p class="text-light mt-2">正在启动摄像头...</p>
      </div>
      
      <!-- Error Overlay -->
      <div v-if="error" class="camera-overlay error">
        <i class="bi bi-exclamation-circle text-danger mb-2" style="font-size: 2rem;"></i>
        <p class="text-white">{{ error }}</p>
        <common-button theme="light" size="sm" @click="startCamera" class="mt-2">重试</common-button>
      </div>
    </div>

    <!-- Controls -->
    <div class="camera-controls text-center">
      <div v-if="!isStreaming" class="start-controls">
        <common-button
          theme="primary" 
          size="md"
          @click="startCamera"
        >
           <i class="bi bi-camera-video-fill me-2"></i>开启摄像头
        </common-button>
      </div>
      
      <div v-else class="active-controls">
        <div class="d-flex justify-content-center gap-3 align-items-center">
          <common-button 
            :theme="isDetecting ? 'danger' : 'success'" 
            size="md"
            @click="toggleDetection"
          >
            <i :class="isDetecting ? 'bi bi-stop-circle-fill' : 'bi bi-play-circle-fill'" class="me-2"></i>
            {{ isDetecting ? '停止识别' : '开始实时识别' }}
          </common-button>
          
          <common-button 
            theme="cancel" 
            size="md"
            @click="stopCamera"
          >
            <i class="bi bi-camera-video-off-fill me-2"></i>关闭摄像头
          </common-button>
        </div>
        
        <p v-if="isDetecting" class="text-success mt-2 mb-0 small">
          <span class="spinner-grow spinner-grow-sm me-1" role="status"></span>
          正在实时分析中...
        </p>
      </div>
    </div>

    <!-- Results Summary -->
    <div v-if="isStreaming" class="camera-results-container mt-4">
      <h6 class="mb-3 d-flex align-items-center">
        <i class="bi bi-list-columns-reverse me-2 text-primary"></i>
        检测历史
      </h6>
      
      <div class="results-list-wrapper">
        <div v-if="detectionHistory.length > 0" class="table-responsive">
          <table class="table table-sm align-middle result-table">
            <thead>
              <tr>
                <th style="width: 30%">物品名称</th>
                <th style="width: 45%">信心度</th>
                <th style="width: 25%">位置</th>
              </tr>
            </thead>
            <tbody>
              <transition-group name="list">
                <tr v-for="item in detectionHistory" :key="item.id">
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
                    <span v-else class="text-muted small">极低信心度</span>
                  </td>
                  <td class="text-muted font-monospace small">
                    {{
                      item.bbox
                        ? `[${Math.round(item.bbox[0])}, ${Math.round(item.bbox[1])}]`
                        : 'N/A'
                    }}
                  </td>
                </tr>
              </transition-group>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-4 text-muted">
          <i class="bi bi-search mb-2 d-block" style="font-size: 1.5rem; opacity: 0.5;"></i>
          等待检测结果...
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, computed, watch } from 'vue';
import CommonButton from '@/components/CommonButton.vue';
import { useApi } from '@/composables/useApi';
import '../styles/components/progress.css';
import '../styles/components/labels.css';

const props = defineProps({
  detectionInterval: {
    type: Number,
    default: 500 // ms between frames
  }
});

const emit = defineEmits(['error']);

const { detect } = useApi();

const videoRef = ref(null);
const canvasRef = ref(null);
const stream = ref(null);
const isStreaming = ref(false);
const isInitializing = ref(false);
const isDetecting = ref(false);
const isProcessing = ref(false); // Throttle flag
const error = ref('');
const lastResult = ref(null);
const detectionHistory = ref([]); // Store last 10 detections

let detectionTimer = null;
let offscreenCanvas = null;

// Categories for classification labels
const getCategoryClass = (className) => {
  const classMap = {
    '可回收垃圾': 'recyclable',
    '有害垃圾': 'harmful',
    '厨余垃圾': 'kitchen',
    '其他垃圾': 'other',
  }
  // Backward compatibility
  if (className === '可回收') return 'recyclable'
  if (className === '有害') return 'harmful'
  if (className === '厨余') return 'kitchen'
  if (className === '其他') return 'other'

  return classMap[className] || 'other'
}

// Progress bar color based on confidence
const getProgressLevelClass = (confidence) => {
  if (confidence >= 0.9) return 'lvl-excellent'
  if (confidence >= 0.7) return 'lvl-high'
  if (confidence >= 0.4) return 'lvl-medium'
  return 'lvl-low'
};

const startCamera = async () => {
  error.value = '';
  isInitializing.value = true;
  try {
    const constraints = {
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'environment' }
    };
    stream.value = await navigator.mediaDevices.getUserMedia(constraints);
    if (videoRef.value) {
      videoRef.value.srcObject = stream.value;
      videoRef.value.onloadedmetadata = () => {
        isInitializing.value = false;
        isStreaming.value = true;
        resizeCanvas();
      };
    }
  } catch (err) {
    console.error('Camera access error:', err);
    error.value = '无法访问摄像头，请确保已授予权限。';
    isInitializing.value = false;
    emit('error', err);
  }
};

const stopCamera = () => {
  stopDetection();
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop());
    stream.value = null;
  }
  if (videoRef.value) videoRef.value.srcObject = null;
  isStreaming.value = false;
  const ctx = canvasRef.value?.getContext('2d');
  if (ctx && canvasRef.value) {
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
  }
};

const resizeCanvas = () => {
  if (videoRef.value && canvasRef.value) {
    canvasRef.value.width = videoRef.value.videoWidth;
    canvasRef.value.height = videoRef.value.videoHeight;
  }
};

const toggleDetection = () => {
  if (isDetecting.value) stopDetection();
  else startDetection();
};

const startDetection = () => {
  if (!isStreaming.value) return;
  isDetecting.value = true;
  detectFrame();
  detectionTimer = setInterval(detectFrame, props.detectionInterval);
};

const stopDetection = () => {
  isDetecting.value = false;
  if (detectionTimer) {
    clearInterval(detectionTimer);
    detectionTimer = null;
  }
  const ctx = canvasRef.value?.getContext('2d');
  if (ctx && canvasRef.value) {
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
  }
};

const detectFrame = async () => {
  if (!videoRef.value || !canvasRef.value || !isDetecting.value || isProcessing.value) return;

  isProcessing.value = true;
  const video = videoRef.value;
  
  if (!offscreenCanvas) offscreenCanvas = document.createElement('canvas');
  if (offscreenCanvas.width !== video.videoWidth || offscreenCanvas.height !== video.videoHeight) {
    offscreenCanvas.width = video.videoWidth;
    offscreenCanvas.height = video.videoHeight;
  }
  
  const ctx = offscreenCanvas.getContext('2d');
  ctx.drawImage(video, 0, 0, offscreenCanvas.width, offscreenCanvas.height);
  
  offscreenCanvas.toBlob(async (blob) => {
    if (!blob) {
      isProcessing.value = false;
      return;
    }
    const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
    try {
      const result = await detect(file);
      console.log('DEBUG: Camera detection result:', result);
      lastResult.value = result;
      if (result.results && result.results.length > 0) {
        console.log('DEBUG: Objects detected count:', result.results.length);
        result.results.forEach(item => {
          console.log(`DEBUG: Detected [${item.class_name}] with confidence ${item.confidence}`);
          detectionHistory.value.unshift({ ...item, id: Date.now() + Math.random() });
          if (detectionHistory.value.length > 10) detectionHistory.value.pop();
        });
      }
      drawResults(result);
    } catch (err) {
      console.error('Detection error:', err);
    } finally {
      isProcessing.value = false;
    }
  }, 'image/jpeg', 0.8);
};

const drawResults = (data) => {
  if (!canvasRef.value || !videoRef.value) return;
  const ctx = canvasRef.value.getContext('2d');
  const canvasWidth = canvasRef.value.width;
  const canvasHeight = canvasRef.value.height;
  ctx.clearRect(0, 0, canvasWidth, canvasHeight);
  if (!data.results || data.results.length === 0) return;

  data.results.forEach(item => {
    if (!item.bbox) return;
    const [x1, y1, x2, y2] = item.bbox;
    const width = x2 - x1;
    const height = y2 - y1;
    let color = '#6c757d';
    if (item.class_name.includes('可回收垃圾')) color = '#3576ca';
    if (item.class_name.includes('有害垃圾')) color = '#dc3545';
    if (item.class_name.includes('厨余垃圾')) color = '#28a745';
    
    ctx.strokeStyle = color;
    ctx.lineWidth = 4;
    ctx.strokeRect(x1, y1, width, height);
    ctx.fillStyle = color;
    const text = `${item.class_name} ${(item.confidence * 100).toFixed(0)}%`;
    const textWidth = ctx.measureText(text).width;
    ctx.fillRect(x1, y1 - 25, textWidth + 10, 25);
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 16px Arial';
    ctx.fillText(text, x1 + 5, y1 - 7);
  });
};

const handleResize = () => {
  if (isStreaming.value) resizeCanvas();
};

import { onMounted } from 'vue';
onMounted(() => {
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  stopCamera();
});
</script>

<style scoped>
.camera-detect-container {
  max-width: 800px;
  margin: 0 auto;
}

.camera-viewport {
  position: relative;
  width: 100%;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  aspect-ratio: 4/3; /* Standard camera aspect */
}

.camera-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.camera-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none; /* Let clicks pass through if needed */
}

.camera-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

/* Results List Styles */
.results-list-wrapper {
  max-height: 400px;
  overflow-y: auto;
  background: #fff;
  border-radius: 12px;
  border: 1px solid rgba(0,0,0,0.05);
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

.result-table {
  margin-bottom: 0;
}

.result-table th {
  background: #f8f9fa;
  padding: 12px 15px;
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 600;
  border-top: none;
}

.result-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #f1f1f1;
}

/* Category labels moved to shared labels.css component */

/* Custom Scrollbar for the results list */
.results-list-wrapper::-webkit-scrollbar {
  width: 6px;
}
.results-list-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}
.results-list-wrapper::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 10px;
}
.results-list-wrapper::-webkit-scrollbar-thumb:hover {
  background: #999;
}

/* List Transitions */
.list-enter-active,
.list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
