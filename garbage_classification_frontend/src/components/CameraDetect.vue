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
         <common-button theme="primary" @click="startCamera">
           <i class="bi bi-camera-video-fill me-2"></i>开启摄像头
         </common-button>
      </div>
      
      <div v-else class="active-controls">
        <div class="d-flex justify-content-center gap-3 align-items-center">
          <common-button 
            :theme="isDetecting ? 'danger' : 'success'" 
            @click="toggleDetection"
          >
            <i :class="isDetecting ? 'bi bi-stop-circle-fill' : 'bi bi-play-circle-fill'" class="me-2"></i>
            {{ isDetecting ? '停止识别' : '开始实时识别' }}
          </common-button>
          
          <common-button theme="secondary" @click="stopCamera">
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
    <div v-if="lastResult && isDetecting" class="camera-result-summary mt-3">
      <div v-if="formattedResults.length > 0" class="d-flex flex-wrap justify-content-center gap-2">
        <span 
          v-for="(item, idx) in formattedResults" 
          :key="idx" 
          :class="`badge rounded-pill bg-${getCategoryColor(item.class_name)}`"
          style="font-size: 0.9rem; padding: 0.5em 1em;"
        >
          {{ item.class_name }} {{ (item.confidence * 100).toFixed(0) }}%
        </span>
      </div>
      <div v-else class="text-muted small">
        暂未检测到目标
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, computed, watch } from 'vue';
import CommonButton from '@/components/CommonButton.vue';
import { useApi } from '@/composables/useApi';

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
const error = ref('');
const lastResult = ref(null);

let detectionTimer = null;

// Categories for badge colors
const getCategoryColor = (name) => {
  if (name.includes('可回收')) return 'primary';
  if (name.includes('有害')) return 'danger';
  if (name.includes('厨余')) return 'success';
  return 'secondary'; // 其他
};

const formattedResults = computed(() => {
  if (!lastResult.value?.results) return [];
  return lastResult.value.results;
});

const startCamera = async () => {
  error.value = '';
  isInitializing.value = true;
  
  try {
    const constraints = {
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: 'environment' // Prefer back camera on mobile
      }
    };
    
    stream.value = await navigator.mediaDevices.getUserMedia(constraints);
    
    if (videoRef.value) {
      videoRef.value.srcObject = stream.value;
      // Wait for metadata to load to set canvas dimensions match video
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
  if (videoRef.value) {
    videoRef.value.srcObject = null;
  }
  isStreaming.value = false;
  
  // Clear canvas
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
  if (isDetecting.value) {
    stopDetection();
  } else {
    startDetection();
  }
};

const startDetection = () => {
  if (!isStreaming.value) return;
  isDetecting.value = true;
  detectFrame(); // Immediate first frame
  detectionTimer = setInterval(detectFrame, props.detectionInterval);
};

const stopDetection = () => {
  isDetecting.value = false;
  if (detectionTimer) {
    clearInterval(detectionTimer);
    detectionTimer = null;
  }
  // Clear bounding boxes
  const ctx = canvasRef.value?.getContext('2d');
  if (ctx && canvasRef.value) {
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
  }
};

const detectFrame = async () => {
  if (!videoRef.value || !canvasRef.value || !isDetecting.value) return;

  // 1. Capture frame to a temporary canvas (or use the existing one but be careful not to send drawn boxes)
  // Actually, we can just draw the video frame to an offscreen canvas or the current canvas (clearing it first)
  const video = videoRef.value;
  const canvas = document.createElement('canvas'); // Offscreen canvas for capture
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  
  // 2. Convert to blob/file
  canvas.toBlob(async (blob) => {
    if (!blob) return;
    
    // Create File object to match useApi expectations
    const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
    
    try {
      const result = await detect(file);
      lastResult.value = result;
      drawResults(result);
    } catch (err) {
      console.error('Detection error:', err);
      // Don't stop detection on single frame error, but maybe log it
    }
  }, 'image/jpeg', 0.8);
};

const drawResults = (data) => {
  if (!canvasRef.value || !videoRef.value) return;
  
  const ctx = canvasRef.value.getContext('2d');
  const canvasWidth = canvasRef.value.width;
  const canvasHeight = canvasRef.value.height;
  
  // Clear previous drawings
  ctx.clearRect(0, 0, canvasWidth, canvasHeight);
  
  if (!data.results || data.results.length === 0) return;

  // The backend likely returns bboxes normalized or relative to the original image size sent.
  // Since we sent the full video frame, the bbox coordinates should map directly 1:1.
  
  data.results.forEach(item => {
    if (!item.bbox) return;
    const [x1, y1, x2, y2] = item.bbox;
    const width = x2 - x1;
    const height = y2 - y1;
    
    // Style based on category
    let color = '#6c757d'; // Default grey
    if (item.class_name.includes('可回收')) color = '#007bff'; // Blue
    if (item.class_name.includes('有害')) color = '#dc3545'; // Red
    if (item.class_name.includes('厨余')) color = '#28a745'; // Green
    
    // Draw Box
    ctx.strokeStyle = color;
    ctx.lineWidth = 4;
    ctx.strokeRect(x1, y1, width, height);
    
    // Draw Label Background
    ctx.fillStyle = color;
    const text = `${item.class_name} ${(item.confidence * 100).toFixed(0)}%`;
    const textWidth = ctx.measureText(text).width;
    ctx.fillRect(x1, y1 - 25, textWidth + 10, 25);
    
    // Draw Label Text
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 16px Arial';
    ctx.fillText(text, x1 + 5, y1 - 7);
  });
};

onUnmounted(() => {
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
</style>
