<template>
  <div class="admin-page-wrapper">
    <PageHero
      title="管理后台"
      subtitle="系统数据统计与用户管理"
      ctaText="数据管理"
      ctaLink="#admin-stats-title"
    />
    <div class="admin-content">
    <h2 v-reveal id="admin-stats-title" class="section-title hero-fade-in anim-delay-1">后台数据</h2>
    
    <div v-if="message" :class="`alert alert-${messageType} mb-4`" role="alert">
      {{ message }}
    </div>
    <div class="row">
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <h6 class="text-muted">总检测数</h6>
            <h3>{{ stats.total_detections || 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <h6 class="text-muted">活跃用户</h6>
            <h3>{{ stats.active_users || 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <h6 class="text-muted">平均信心度</h6>
                <div v-if="stats.avg_confidence && stats.avg_confidence > 0" class="gc-progress-container lg mt-2" style="max-width: 280px; margin: 15px auto;">
                  <div
                    class="gc-progress-bar"
                    :class="getProgressLevelClass(stats.avg_confidence)"
                    :style="{ width: `${(stats.avg_confidence * 100).toFixed(1)}%` }"
                  ></div>
                  <span class="gc-progress-label">{{ (stats.avg_confidence * 100).toFixed(1) }}%</span>
                </div>
                <div v-else class="text-muted small my-3">暂无统计数据</div>
                <div class="stat-label">平均识别信心度</div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <h6 class="text-muted">今日活跃</h6>
            <h3>{{ stats.daily_active || 0 }}</h3>
          </div>
        </div>
      </div>
    </div>

    <div class="card mt-4">
      <div class="card-body">
        <h5 class="card-title">类别分布</h5>
        <div v-if="stats.class_distribution">
          <div v-for="(count, className) in stats.class_distribution" :key="className" class="mb-2">
            <div class="d-flex justify-content-between mb-1">
              <span>{{ className }}</span>
              <span>{{ count }}</span>
            </div>
            <div class="progress" style="height: 20px">
              <div
                class="progress-bar"
                :class="`bg-${getColorForClass(className)}`"
                :style="{ width: `${(count / getTotalCount()) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
        <p v-else class="text-muted">暂无数据</p>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import PageHero from '@/components/PageHero.vue'
import '../styles/pages/admin.css'
import '../styles/components/progress.css'

const { getAdminStats } = useApi()

const stats = ref({})
const message = ref('')
const messageType = ref('danger')

const getTotalCount = () => {
  if (!stats.value.class_distribution) return 1
  return Object.values(stats.value.class_distribution).reduce((a, b) => a + b, 0)
}

const getColorForClass = (className) => {
  const colorMap = {
    '可回收垃圾': 'success',
    '有害垃圾': 'danger',
    '厨余垃圾': 'warning',
    '其他垃圾': 'secondary',
  }
  return colorMap[className] || 'primary'
}

const getProgressLevelClass = (confidence) => {
  if (confidence >= 0.9) return 'lvl-excellent'
  if (confidence >= 0.7) return 'lvl-high'
  if (confidence >= 0.4) return 'lvl-medium'
  return 'lvl-low'
}

onMounted(async () => {
  try {
    const result = await getAdminStats()
    if (result.data) {
      stats.value = result.data
    }
  } catch (error) {
    console.error('获取统计失败:', error)
    message.value = '无法加载统计数据，请检查服务状态。'
    messageType.value = 'danger'
  }
})
</script>