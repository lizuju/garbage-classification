<template>
  <div class="admin-page-wrapper">
    <PageHero
      title="管理后台"
      subtitle="系统数据统计与用户管理"
      compact
    />
    <div class="admin-content">
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
            <h3>{{ ((stats.avg_confidence || 0) * 100).toFixed(1) }}%</h3>
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

const { getAdminStats } = useApi()

const stats = ref({})

const getTotalCount = () => {
  if (!stats.value.class_distribution) return 1
  return Object.values(stats.value.class_distribution).reduce((a, b) => a + b, 0)
}

const getColorForClass = (className) => {
  const colorMap = {
    '可回收': 'success',
    '有害': 'danger',
    '厨余': 'warning',
    '其他': 'secondary',
  }
  return colorMap[className] || 'primary'
}

onMounted(async () => {
  try {
    const result = await getAdminStats()
    if (result.data) {
      stats.value = result.data
    }
  } catch (error) {
    console.error('获取统计失败:', error)
  }
})
</script>