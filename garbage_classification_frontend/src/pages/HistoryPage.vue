<template>
  <div v-if="!isLoggedIn" class="container mt-5">
    <div class="alert alert-warning">请先<router-link to="/login">登录</router-link></div>
  </div>

  <div v-else>
    <PageHero
      title="识别历史"
      subtitle="查看您的过往识别记录与分析结果"
      compact
    />
    <div class="history-content">
    <h2 v-reveal id="project-overview" class="section-title hero-fade-in anim-delay-1">垃圾识别</h2>

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
                      <th>检测到的物品数</th>
                      <th>平均信心度</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in history" :key="item.id">
                      <td>{{ formatDate(item.created_at) }}</td>
                      <td>{{ item.detection_count || 0 }} 个</td>
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
                        <button class="btn btn-sm btn-danger" @click="deleteItem(item.id)">
                          <i class="bi bi-trash"></i> 删除
                        </button>
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
import '../styles/pages/history.css'

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

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  console.log('【HistoryPage】组件已挂载，开始加载历史');
  loadHistory()
})
</script>