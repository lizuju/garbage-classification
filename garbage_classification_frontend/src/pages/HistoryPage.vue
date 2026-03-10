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
                       <th>物品类别</th>
                       <th>物品名称</th>
                       <th>信心度</th>
                       <th>操作</th>
                     </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in history" :key="item.id">
                      <td>{{ formatDate(item.created_at) }}</td>
                       <td>{{ item.detection_count || 0 }} 个</td>
                       <td>
                         <span v-if="getTopItem(item.results)" :class="`category-label ${getCategoryClass(getTopItem(item.results).class_name)}`">
                           {{ getMajorCategory(getTopItem(item.results).class_name) }}
                         </span>
                         <span v-else class="text-muted small">无识别数据</span>
                       </td>
                       <td>
                         <span v-if="getTopItem(item.results)">{{ getItemName(getTopItem(item.results).class_name) }}</span>
                         <span v-else class="text-muted small">无识别数据</span>
                       </td>
                       <td>
                         <div v-if="getTopConfidence(item.results) > 0" class="gc-progress-container">
                           <div
                             class="gc-progress-bar"
                             :class="getProgressLevelClass(getTopConfidence(item.results))"
                             :style="{ width: `${(getTopConfidence(item.results) * 100).toFixed(1)}%` }"
                           ></div>
                           <span class="gc-progress-label">{{ (getTopConfidence(item.results) * 100).toFixed(1) }}%</span>
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
  const major = getMajorCategory(className)
  const classMap = {
    '可回收物': 'recyclable',
    '有害垃圾': 'harmful',
    '厨余垃圾': 'kitchen',
    '其他垃圾': 'other',
  }
  return classMap[major] || 'other'
}

const getMajorCategory = (className) => {
  const name = className || ''
  if (name.includes('可回收')) return '可回收物'
  if (name.includes('有害')) return '有害垃圾'
  if (name.includes('厨余')) return '厨余垃圾'
  return '其他垃圾'
}

const getItemName = (className) => {
  const name = className || ''
  return name
    .replace(/^(可回收物|有害垃圾|厨余垃圾|其他垃圾)[-_：: ]*/g, '')
    .trim() || name
}

const getTopItem = (results) => {
  if (!results || !Array.isArray(results) || results.length === 0) return null
  return [...results].sort((a, b) => (b.confidence || 0) - (a.confidence || 0))[0]
}

const getTopConfidence = (results) => {
  const top = getTopItem(results)
  return top && top.confidence ? top.confidence : 0
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
