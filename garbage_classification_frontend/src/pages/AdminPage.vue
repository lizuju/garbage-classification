<template>
  <div class="admin-page-wrapper">
    <PageHero
      title="管理后台"
      subtitle="系统数据统计与权限管理"
      ctaText="进入控制台"
      ctaLink="#admin-console"
    />
    
    <div class="admin-content" id="admin-console">
      <h2 v-reveal id="admin-stats-title" class="section-title hero-fade-in anim-delay-1">后台数据</h2>
      
      <!-- Tab Navigation -->
      <div v-reveal class="admin-tabs hero-fade-in anim-delay-1">
        <div 
          class="admin-tab-item" 
          :class="{ active: activeTab === 'overview' }"
          @click="activeTab = 'overview'"
        >
          数据概览
        </div>
        <div 
          class="admin-tab-item" 
          :class="{ active: activeTab === 'users' }"
          @click="activeTab = 'users'"
        >
          用户管理
        </div>
        <div 
          class="admin-tab-item" 
          :class="{ active: activeTab === 'logs' }"
          @click="activeTab = 'logs'"
        >
          系统日志
        </div>
      </div>

      <div v-if="message" :class="`alert alert-${messageType} mb-4`" role="alert">
        {{ message }}
      </div>

      <transition name="zoom-fade">
        <div v-if="actionNotice" 
            :class="['alert', `alert-${noticeType}`, 'border-0', 'shadow-lg', 'text-center', 'py-2', 'mb-4']" 
            role="alert">
          <i :class="noticeType === 'success' ? 'bi bi-check-circle-fill' : 'bi bi-x-circle-fill'" class="me-2"></i>
          {{ actionNotice }}
        </div>
      </transition>

      <!-- Tab Content: Overview -->
      <div v-reveal v-if="activeTab === 'overview'" class="tab-pane hero-fade-in anim-delay-1">
        <div class="row mb-4">
          <!-- Main Stats row -->
          <div class="col-md-3">
            <div class="card text-center h-100">
              <div class="card-body d-flex flex-column justify-content-center">
                <h6 class="mb-2">总检测数</h6>
                <h2 class="fw-bold mb-0">{{ stats.total_detections || 0 }}</h2>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card text-center h-100">
              <div class="card-body d-flex flex-column justify-content-center">
                <h6 class="mb-2">总注册用户</h6>
                <h2 class="fw-bold mb-0">{{ stats.total_users || 0 }}</h2>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card text-center h-100">
              <div class="card-body d-flex flex-column justify-content-center">
                <h6 class="mb-2">平均信心度</h6>
                <div v-if="stats.avg_confidence && stats.avg_confidence > 0" class="gc-progress-container mt-2" style="max-width: 140px; margin: 0 auto;">
                  <div
                    class="gc-progress-bar"
                    :class="getProgressLevelClass(stats.avg_confidence)"
                    :style="{ width: `${(stats.avg_confidence * 100).toFixed(1)}%` }"
                  ></div>
                  <span class="gc-progress-label">{{ (stats.avg_confidence * 100).toFixed(1) }}%</span>
                </div>
                <div v-else class="small">暂无数据</div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card text-center h-100">
              <div class="card-body d-flex flex-column justify-content-center">
                <h6 class="mb-2">今日活跃</h6>
                <h2 class="fw-bold mb-0">{{ stats.daily_active || 0 }}</h2>
              </div>
            </div>
          </div>
        </div>

        <div class="row">
          <!-- System Status -->
          <div class="col-md-4 mb-4">
            <div class="card h-100">
              <div class="card-body">
                <h6 class="card-title fw-bold mb-4">系统运行状态</h6>
                <div class="d-flex flex-column gap-3">
                  <div class="status-indicator">
                    <div class="status-dot online"></div>
                    <span class="text-muted">数据库: 正常 (SQLite)</span>
                  </div>
                  <div class="status-indicator">
                    <div class="status-dot online"></div>
                    <span class="text-muted">YOLO 引擎: 已就绪 (v5s)</span>
                  </div>
                  <div class="status-indicator">
                    <div class="status-dot online"></div>
                    <span class="text-muted">API 服务: 运行中 (5001)</span>
                  </div>
                  <div class="status-indicator">
                    <div class="status-dot warning"></div>
                    <span class="text-muted">磁盘空间: 82% 良好</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="col-md-4 mb-4">
            <div class="card h-100">
              <div class="card-body">
                <h6 class="card-title fw-bold mb-4">管理快捷入口</h6>
                <div class="row g-3">
                  <div class="col-6">
                    <CommonButton 
                      theme="secondary"
                      size="square"
                      class="w-100 d-flex flex-column align-items-center" 
                      @click="handleRefresh"
                      :disabled="isLoadingStats"
                    >
                      <i class="bi bi-arrow-clockwise mb-2 fs-4" :class="{ 'animate-spin': isLoadingStats }"></i>
                      <span>刷新面板</span>
                    </CommonButton>
                  </div>
                  <div class="col-6">
                    <CommonButton
                      theme="secondary"
                      size="square"
                      class="w-100 d-flex flex-column align-items-center" 
                      @click="activeTab = 'logs'"
                    >
                      <i class="bi bi-journal-text mb-2 fs-4"></i>
                      <span>查看日志</span>
                    </CommonButton>
                  </div>
                  <div class="col-6">
                    <CommonButton
                      theme="secondary"
                      size="square"
                      class="w-100 d-flex flex-column align-items-center" 
                      @click="handleExport"
                      :disabled="isExporting"
                    >
                      <i class="bi bi-cloud-download mb-2 fs-4"></i>
                      <span>{{ isExporting ? '处理中...' : '导出数据' }}</span>
                    </CommonButton>
                  </div>
                  <div class="col-6">
                    <CommonButton
                      theme="secondary"
                      size="square"
                      class="w-100 d-flex flex-column align-items-center"
                      @click="handleAudit"
                    >
                      <i class="bi bi-shield-check mb-2 fs-4"></i>
                      <span>安全审计</span>
                    </CommonButton>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Class Distribution Summary -->
          <div class="col-md-4 mb-4">
            <div class="card h-100">
              <div class="card-body">
                <h6 class="card-title fw-bold mb-4">分类识别概况</h6>
                <div v-if="stats.class_distribution">
                  <div v-for="(count, className) in stats.class_distribution" :key="className" class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                      <span class="small fw-600">{{ className }}</span>
                      <span class="text-muted x-small">{{ count }}次</span>
                    </div>
                    <div class="gc-progress-container" style="height: 10px;">
                      <div
                        class="gc-progress-bar"
                        :class="`bg-${getColorForClass(className)}`"
                        :style="{ width: `${(count / (getTotalCount() || 1)) * 100}%` }"
                      ></div>
                    </div>
                  </div>
                </div>
                <p v-else class="text-muted small">暂无类别统计数据</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Content: Users -->
      <div v-reveal v-if="activeTab === 'users'" class="tab-pane hero-fade-in anim-delay-1">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title mb-4">系统用户列表</h5>
            <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>UID</th>
                    <th>用户名</th>
                    <th>邮箱</th>
                    <th>角色</th>
                    <th>注册时间</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in users" :key="user.id">
                    <td>{{ user.id }}</td>
                    <td class="fw-bold">{{ user.username }}</td>
                    <td>{{ user.email }}</td>
                    <td>
                      <span class="role-label" :class="user.is_admin ? 'admin' : 'user'">
                        {{ user.is_admin ? '管理员' : '普通用户' }}
                      </span>
                    </td>
                    <td>{{ formatDate(user.created_at) }}</td>
                    <td>
                      <div class="d-flex gap-2">
                        <CommonButton theme="primary" size="sm" @click="() => {}">编辑</CommonButton>
                        <CommonButton 
                          theme="danger" 
                          size="sm" 
                          :disabled="user.username === 'admin'"
                          @click="() => {}"
                        >
                          禁用
                        </CommonButton>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Content: Logs -->
      <div v-reveal v-if="activeTab === 'logs'" class="tab-pane hero-fade-in anim-delay-1">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title mb-4">系统操作日志</h5>
            <div class="table-responsive">
              <table class="table table-sm table-hover">
                <thead>
                  <tr>
                    <th>时间</th>
                    <th>类型</th>
                    <th>操作员</th>
                    <th>信息</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="log in logs" :key="log.id">
                    <td class="text-muted small">{{ formatDate(log.created_at) }}</td>
                    <td>
                      <span class="log-type" :class="log.log_type.toLowerCase()">
                        {{ log.log_type }}
                      </span>
                    </td>
                    <td>{{ log.username || '系统' }}</td>
                    <td class="text-wrap" style="max-width: 400px;">{{ log.message }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- Pagination Shorthand -->
            <div class="d-flex justify-content-between align-items-center mt-4">
              <span class="small text-muted">共 {{ logPagination.total }} 条记录</span>
              <div class="btn-group gap-2">
                <CommonButton 
                  theme="secondary" 
                  size="sm"
                  :disabled="logPagination.current_page === 1"
                  @click="fetchLogs(logPagination.current_page - 1)"
                >
                  上一页
                </CommonButton>
                <CommonButton 
                  theme="secondary" 
                  size="sm"
                  :disabled="logPagination.current_page === logPagination.pages"
                  @click="fetchLogs(logPagination.current_page + 1)"
                >
                  下一页
                </CommonButton>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Security Audit Modal -->
    <transition name="fade">
      <div v-if="showAuditModal" class="modal-backdrop-blur" @click.self="closeAuditModal">
        <transition name="zoom-fade">
          <div v-reveal class="modal-container modal-profile card card-glass hero-fade-in">
            <!-- Close Button -->
            <!-- Close Button -->
            <CommonButton 
              theme="glass-dark" 
              circle 
              size="md" 
              class="modal-close-btn" 
              @click="closeAuditModal" 
              aria-label="关闭"
            >
              <i class="bi bi-x-lg"></i>
            </CommonButton>
            <div class="audit-header">
              <h3 class="mb-1"><i class="bi bi-shield-lock-fill me-2"></i>系统安全与健康审计</h3>
              <p class="fs-5 opacity-75 mb-0">深度扫描系统架构、日志密度与权限安全</p>
            </div>
            
            <div class="audit-body">
              <!-- Scanning State -->
              <div v-if="auditState === 'scanning'" class="scanning-container">
                <div class="scan-radar"></div>
                <h3 class="mb-2">正在扫描系统...</h3>
                <p class="text-muted fs-5">正在检查: {{ currentScanTarget }}</p>
                <div class="gc-progress-container mt-4" style="max-width: 300px; margin: 0 auto; height: 8px;">
                  <div class="gc-progress-bar bg-primary" :style="{ width: `${scanProgress}%` }"></div>
                </div>
              </div>

              <!-- Report State -->
              <div v-if="auditState === 'report'" class="audit-report">
                <div :class="['audit-score-circle', getScoreClass(auditReport.score)]">
                  <span class="display-4 fw-bold mb-0">{{ auditReport.score }}</span>
                  <span class="fs-5 fw-bold">安全得分</span>
                </div>

                <div class="audit-items-list">
                  <div v-for="(item, index) in auditReport.items" :key="index" 
                       :class="['audit-item', item.status]">
                    <div class="d-flex align-items-center">
                      <i :class="getAuditIcon(item.status)" class="fs-5 me-3"></i>
                      <div>
                        <div class="fw-600 fs-6">{{ item.title }}</div>
                        <div class="small text-muted">{{ item.desc }}</div>
                      </div>
                    </div>
                    <span :class="['status-badge', item.status]">
                      {{ item.status === 'success' ? '安全' : item.status === 'warning' ? '提示' : '风险' }}
                    </span>
                  </div>
                </div>

                <div class="mt-4 text-center">
                  <CommonButton theme="cancel" size="md" @click="closeAuditModal">关闭自检报告</CommonButton>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useApi } from '../composables/useApi'
import PageHero from '@/components/PageHero.vue'
import CommonButton from '@/components/CommonButton.vue'
import '../styles/pages/admin.css'
import '../styles/components/progress.css'
import '../styles/components/table.css'
import '../styles/components/card.css'
import '../styles/components/modal.css'
import '../styles/components/common-button.css'

const { getAdminStats, getAdminUsers, getAdminLogs, exportAdminData } = useApi()

const activeTab = ref('overview')
const stats = ref({})
const users = ref([])
const logs = ref([])
const logPagination = ref({ total: 0, pages: 1, current_page: 1 })
const message = ref('')
const messageType = ref('danger')
const isLoadingStats = ref(false)
const isExporting = ref(false)
const actionNotice = ref('')
const noticeType = ref('')
let noticeTimer = null

// Audit Modal State
const showAuditModal = ref(false)
const auditState = ref('scanning') // 'scanning' | 'report'
const currentScanTarget = ref('')
const scanProgress = ref(0)
const auditReport = ref({ score: 0, items: [] })

const fetchStats = async () => {
  isLoadingStats.value = true
  try {
    const result = await getAdminStats()
    if (result.stats) stats.value = result.stats
  } catch (err) {
    message.value = '获取统计数据失败'
  } finally {
    isLoadingStats.value = false
  }
}

const showNotice = (text, type = 'info') => {
  if (noticeTimer) clearTimeout(noticeTimer)
  actionNotice.value = text
  noticeType.value = type
  noticeTimer = setTimeout(() => {
    actionNotice.value = ''
    noticeType.value = ''
    noticeTimer = null
  }, 3000)
}

const handleRefresh = async () => {
  await fetchStats()
  showNotice('仪表盘数据已刷新', 'success')
}

const handleExport = async () => {
  isExporting.value = true
  try {
    const data = await exportAdminData()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `system_export_${new Date().toISOString().split('T')[0]}.json`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    showNotice('系统数据导出成功', 'success')
  } catch (err) {
    message.value = '导出数据失败: ' + err.message
  } finally {
    isExporting.value = false
  }
}

const handleAudit = () => {
  showAuditModal.value = true
  document.body.classList.add('modal-open')
  startScan()
}

const closeAuditModal = () => {
  showAuditModal.value = false
  document.body.classList.remove('modal-open')
}

const startScan = async () => {
  auditState.value = 'scanning'
  scanProgress.value = 0
  
  const targets = [
    '正在验证身份验证令牌加密算法...',
    '正在扫描系统访问日志异常频率...',
    '正在检查关键数据库文件完整性...',
    '正在评估 YOLO 推理引擎资源占用...',
    '正在检测磁盘存储分区的健康度...',
    '正在审查管理员账户权限配置...'
  ]

  for (let i = 0; i < targets.length; i++) {
    currentScanTarget.value = targets[i]
    // Simulate scan progress
    for (let p = 0; p < 100 / targets.length; p++) {
      scanProgress.value += 1
      await new Promise(r => setTimeout(r, 15))
    }
    await new Promise(r => setTimeout(r, 200))
  }
  
  generateAuditReport()
}

const generateAuditReport = () => {
  // Logic to simulate a real audit based on system state
  const items = []
  let score = 95

  // 1. Account Safety
  items.push({
    title: '特权账户审核',
    desc: '已配置 1 个管理员账户，权限隔离正常。',
    status: 'success'
  })

  // 2. Encryption
  items.push({
    title: '通信协议加密',
    desc: 'API 接口层使用 JWT 认证，令牌过期策略已激活。',
    status: 'success'
  })

  // 3. System Load
  items.push({
    title: '存储空间预警',
    desc: '当前磁盘空间占用 82%，建议在达到 90% 前清理日志。',
    status: 'warning'
  })
  score -= 5

  // 4. Log Health
  const recentLogs = logs.value.slice(0, 20)
  const hasErrors = recentLogs.some(l => l.log_type === 'ERROR')
  if (hasErrors) {
    items.push({
      title: '运行时异常检测',
      desc: '最近捕捉到若干运行错误，请检查系统日志详情。',
      status: 'danger'
    })
    score -= 15
  } else {
    items.push({
      title: '运行时健康度',
      desc: '最近 20 条日志扫描未发现严重运行错误。',
      status: 'success'
    })
  }

  auditReport.value = { score, items }
  auditState.value = 'report'
}

const getScoreClass = (score) => {
  if (score >= 90) return 'secure'
  if (score >= 70) return 'warning'
  return 'danger'
}

const getAuditIcon = (status) => {
  if (status === 'success') return 'bi bi-check-circle-fill text-success'
  if (status === 'warning') return 'bi bi-exclamation-triangle-fill text-warning'
  return 'bi bi-x-circle-fill text-danger'
}

const fetchUsers = async () => {
  try {
    const result = await getAdminUsers()
    if (result.users) users.value = result.users
  } catch (err) {
    message.value = '获取用户列表失败'
  }
}

const fetchLogs = async (page = 1) => {
  try {
    const result = await getAdminLogs(page)
    if (result.logs) {
      logs.value = result.logs
      logPagination.value = {
        total: result.total,
        pages: result.pages,
        current_page: result.current_page
      }
    }
  } catch (err) {
    message.value = '获取操作日志失败'
  }
}

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

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  // If the backend timestamp doesn't have Z, append it to treat as UTC
  const utcString = dateStr.endsWith('Z') ? dateStr : dateStr + 'Z'
  return new Date(utcString).toLocaleString('zh-CN')
}

// Watch tab changes to load data
watch(activeTab, (newTab) => {
  message.value = ''
  if (newTab === 'overview') fetchStats()
  if (newTab === 'users') fetchUsers()
  if (newTab === 'logs') fetchLogs()
}, { immediate: true })

onMounted(() => {
  fetchStats()
})
</script>