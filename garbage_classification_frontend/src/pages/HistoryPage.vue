<template>
  <div v-if="!isLoggedIn" class="container mt-5">
    <div class="alert alert-warning">请先<router-link to="/login">登录</router-link></div>
  </div>

  <div v-else>
    <PageHero
      title="识别历史"
      subtitle="查看您的过往识别记录与分析结果"
      ctaText="查看记录"
      ctaLink="#history-records"
    />
    <div class="history-content">
    <h2 v-reveal id="history-records" class="section-title hero-fade-in anim-delay-1">历史记录</h2>

    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div class="card-body">

            <div v-if="message" :class="`alert alert-${messageType} mb-3`">
              {{ message }}
            </div>

            <div v-if="isLoading" class="text-center p-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
              </div>
            </div>

            <div v-else-if="history && history.length > 0">
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                     <tr>
                       <th>时间</th>
                       <th>检测记录</th>
                       <th>识别物品</th>
                       <th>平均信心度</th>
                       <th>操作</th>
                     </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in history" :key="item.id">
                      <td>{{ formatDate(item.created_at) }}</td>
                       <td>{{ item.detection_count || 0 }} 个</td>
                       <td>
                         <div class="d-flex flex-wrap gap-1">
                           <span 
                             v-for="(res, ridx) in getUniqueCategories(item.results)" 
                             :key="ridx"
                             :class="`category-label ${getCategoryClass(res)}`"
                           >
                             {{ res }}
                           </span>
                         </div>
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
                         <span v-else class="text-muted small">无识别数据</span>
                       </td>
                      <td>
                        <CommonButton theme="danger" size="sm" @click="deleteItem(item.id)">
                          <i class="bi bi-trash"></i> 删除
                        </CommonButton>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div v-else class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>还没有识别历史记录，<router-link to="/user/detect">开始识别</router-link>一张图片吧！
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
import PageHero from '@/components/PageHero.vue'
import CommonButton from '@/components/CommonButton.vue'
import '../styles/pages/history.css'
import '../styles/components/progress.css'
import '../styles/components/labels.css'

const { isLoggedIn } = useAuth()
const { getHistory, deleteHistory } = useApi()

const history = ref([])
const isLoading = ref(false)
const message = ref('')
const messageType = ref('')

const loadHistory = async () => {
  isLoading.value = true
  try {
    const result = await getHistory()
    console.log('【HistoryPage】后端返回的历史数据:', result);

    if (result.data) {
      history.value = result.data
    }
  } catch (error) {
    console.error('【HistoryPage】加载出错:', error);
    message.value = error.message || '加载失败'
    messageType.value = 'danger'
  } finally {
    isLoading.value = false
  }
}

const deleteItem = async (id) => {
  if (!confirm('确定要删除这条记录吗？')) return

  try {
    await deleteHistory(id)
    message.value = '删除成功'
    messageType.value = 'success'
    await loadHistory()
  } catch (error) {
    message.value = error.message || '删除失败'
    messageType.value = 'danger'
  }
}

const getCategoryClass = (className) => {
  const classMap = {
    '可回收垃圾': 'recyclable',
    '有害垃圾': 'harmful',
    '厨余垃圾': 'kitchen',
    '其他垃圾': 'other',
  }
  // Backward compatibility also needed here
  if (className === '可回收') return 'recyclable'
  if (className === '有害') return 'harmful'
  if (className === '厨余') return 'kitchen'
  if (className === '其他') return 'other'
  
  return classMap[className] || 'other'
}

const getUniqueCategories = (results) => {
  if (!results || !Array.isArray(results)) return []
  return [...new Set(results.map(r => r.class_name))]
}

const getProgressLevelClass = (confidence) => {
  if (confidence >= 0.9) return 'lvl-excellent'
  if (confidence >= 0.7) return 'lvl-high'
  if (confidence >= 0.4) return 'lvl-medium'
  return 'lvl-low'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  // If the backend hasn't been restarted yet, this fix ensures it's treated as UTC
  const utcString = dateString.endsWith('Z') ? dateString : dateString + 'Z'
  return new Date(utcString).toLocaleString('zh-CN')
}

onMounted(() => {
  console.log('【HistoryPage】组件已挂载，开始加载历史');
  loadHistory()
})
</script>