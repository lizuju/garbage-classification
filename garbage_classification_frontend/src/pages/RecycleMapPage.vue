<template>
  <div class="recycle-map-page-wrapper">
    <PageHero
      title="回收地图"
      subtitle="查看附近回收点与投放建议"
      ctaText="查看回收点"
      ctaLink="#recycle-navigation"
    />

    <div class="recycle-map-content">
      <h2 v-reveal id="recycle-navigation" class="section-title hero-fade-in anim-delay-1">导航回收</h2>
      <div class="card card-glass">
        <div class="card-body p-4 p-md-5">
          <h3 class="card-title mb-3">回收点地图</h3>
          <p class="text-muted mb-4">
            基于高德地图展示你附近的回收站点、地址与距离信息。
          </p>

          <div v-if="errorMessage" class="alert alert-warning mb-4">
            {{ errorMessage }}
          </div>

          <div class="mb-3 d-flex gap-2">
            <select v-model.number="selectedRadius" class="form-select w-auto" :disabled="isLoading">
              <option v-for="opt in radiusOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>

            <select v-model="selectedCategory" class="form-select w-auto" :disabled="isLoading">
              <option v-for="opt in categoryOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>

            <CommonButton theme="success" size="md" :disabled="isLoading || !amapReady" @click="locateAndSearch">
              {{ isLoading ? '加载中...' : '重新定位并搜索' }}
            </CommonButton>
          </div>

          <div v-if="statusText" class="small text-muted mb-3">{{ statusText }}</div>
          <div class="recycle-map-main">
            <section class="map-panel">
              <div class="map-shell">
                <div ref="mapContainer" class="map-placeholder"></div>
                <div v-if="isLoading" class="map-loading-overlay">
                  <div class="map-loading-glass">
                    <div class="spinner-border text-primary map-spinner" role="status" aria-hidden="true"></div>
                    <span>正在更新附近回收点...</span>
                  </div>
                </div>
              </div>
            </section>

            <aside class="poi-panel">
              <div v-if="selectedPoi" class="selected-poi-card mb-3">
                <div class="selected-poi-header">
                  <div>
                    <div class="selected-poi-label">当前选中回收点</div>
                    <div class="selected-poi-title">{{ currentPoi?.name || '未命名回收点' }}</div>
                  </div>
                  <span class="selected-poi-badge">高德详情</span>
                </div>

                <div v-if="detailsLoading" class="selected-poi-loading">正在加载更多回收点信息...</div>

                <div class="selected-poi-grid">
                  <div class="selected-poi-meta">
                    <i class="bi bi-geo-alt"></i>
                    <div><span>地址</span>{{ currentPoi?.address || '未知' }}</div>
                  </div>
                  <div class="selected-poi-meta">
                    <i class="bi bi-telephone"></i>
                    <div><span>电话</span>{{ formatTel(currentPoi?.tel) }}</div>
                  </div>
                  <div class="selected-poi-meta">
                    <i class="bi bi-clock-history"></i>
                    <div><span>营业时间</span>{{ formatBusinessHours(currentPoi) }}</div>
                  </div>
                  <div class="selected-poi-meta">
                    <i class="bi bi-star"></i>
                    <div><span>评分</span>{{ formatRating(currentPoi) }}</div>
                  </div>
                  <div class="selected-poi-meta">
                    <i class="bi bi-pin-map"></i>
                    <div><span>区域</span>{{ formatArea(currentPoi) }}</div>
                  </div>
                  <div class="selected-poi-meta">
                    <i class="bi bi-signpost-split"></i>
                    <div><span>距离</span>{{ formatDistance(currentPoi?.distance) }}</div>
                  </div>
                </div>
                <a
                  v-if="navigationUrl"
                  :href="navigationUrl"
                  class="selected-poi-nav-btn"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <i class="bi bi-compass"></i>
                  进入导航
                </a>
              </div>

              <h5 class="mb-3">附近回收点（{{ pois.length }}）</h5>
              <div v-if="!isLoading && pois.length === 0" class="text-muted">
                暂未检索到附近回收点，请尝试重新定位或扩大搜索范围。
              </div>
              <div class="poi-list-scroll">
                <div
                  v-for="(poi, index) in pois"
                  :key="poi.id || index"
                  class="poi-item"
                  :class="{ selected: selectedPoiKey === (poi.id || `${poi.name || ''}_${poi.address || ''}`) }"
                  @click="selectPoi(poi)"
                >
                  <div class="poi-item-main">
                    <div class="poi-title">
                      {{ index + 1 }}. {{ poi.name || '未命名回收点' }}
                    </div>
                    <div class="poi-meta">地址：{{ poi.address || '未知' }}</div>
                  </div>
                  <div class="poi-distance-badge">
                    {{ formatDistance(poi.distance) }}
                  </div>
                </div>
              </div>
            </aside>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, watch } from 'vue'
import PageHero from '@/components/PageHero.vue'
import CommonButton from '@/components/CommonButton.vue'
import { useRecycleMap } from '@/composables/useRecycleMap'
import { RADIUS_OPTIONS, CATEGORY_OPTIONS } from '@/config/recycleMapConfig'
import '../styles/components/card.css'
import '../styles/components/common-button.css'
import '../styles/pages/recycle-map.css';

const {
  mapContainer,
  pois,
  isLoading,
  amapReady,
  errorMessage,
  statusText,
  selectedRadius,
  selectedCategory,
  selectedPoi,
  selectedPoiKey,
  selectedPoiDetails,
  detailsLoading,
  initMap,
  locateAndSearch,
  selectPoi,
  searchWithCurrentSettings,
  destroyMap,
  formatDistance
} = useRecycleMap()
const radiusOptions = RADIUS_OPTIONS
const categoryOptions = CATEGORY_OPTIONS
const currentPoi = computed(() => selectedPoiDetails.value || selectedPoi.value)
const navigationUrl = computed(() => {
  const poi = currentPoi.value
  if (!poi) return ''
  const coords = parseLocation(poi.location)
  if (!coords) return ''
  const [lng, lat] = coords
  const name = encodeURIComponent(poi.name || '回收点')
  return `https://uri.amap.com/navigation?to=${lng},${lat},${name}&mode=car&src=myapp&coordinate=gaode`
})

const parseLocation = (location) => {
  if (!location) return null
  if (typeof location === 'string') {
    const [lng, lat] = location.split(',').map((v) => Number(v))
    if (Number.isFinite(lng) && Number.isFinite(lat)) return [lng, lat]
    return null
  }
  if (typeof location.getLng === 'function' && typeof location.getLat === 'function') {
    return [location.getLng(), location.getLat()]
  }
  if (Array.isArray(location) && location.length >= 2) {
    const [lng, lat] = location
    if (Number.isFinite(Number(lng)) && Number.isFinite(Number(lat))) {
      return [Number(lng), Number(lat)]
    }
  }
  return null
}

const formatBusinessHours = (poi) => {
  if (!poi) return '未知'
  const raw = poi.businessHours || poi.businesshours || poi.opentime
  if (!raw) return '未知'
  return String(raw).replace(/;/g, ' | ')
}

const formatTel = (tel) => {
  if (!tel) return '未知'
  return String(tel).split(';').filter(Boolean).join(' / ')
}

const formatArea = (poi) => {
  if (!poi) return '未知'
  return [poi.pname, poi.cityname, poi.adname].filter(Boolean).join(' ') || '未知'
}

const formatRating = (poi) => {
  if (!poi) return '未知'
  const rating = poi.biz_ext?.rating || poi.rating
  if (!rating || rating === '[]') return '暂无评分'
  return `${rating} / 5`
}

onMounted(async () => {
  try {
    await initMap()
    locateAndSearch()
  } catch (err) {
    errorMessage.value = err.message || '地图初始化失败'
  }
})

watch([selectedRadius, selectedCategory], () => {
  searchWithCurrentSettings()
})

onUnmounted(() => {
  destroyMap()
})
</script>
