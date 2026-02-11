import { ref } from 'vue'
import {
  loadAmap,
  createMap,
  createPlaceSearch,
  getPlaceDetails,
  searchNearBy,
  makeMarker,
  dedupePois,
  setMarkerTheme
} from '@/services/amapService'
import {
  DEFAULT_CENTER,
  CATEGORY_KEYWORDS,
  FALLBACK_KEYWORDS
} from '@/config/recycleMapConfig'

export function useRecycleMap() {
  const mapContainer = ref(null)
  const map = ref(null)
  const placeSearch = ref(null)
  const currentCenterMarker = ref(null)
  const poiMarkers = ref(new Map())
  const selectedPoi = ref(null)
  const selectedPoiKey = ref(null)
  const selectedPoiDetails = ref(null)
  const detailsLoading = ref(false)

  const pois = ref([])
  const isLoading = ref(false)
  const amapReady = ref(false)
  const errorMessage = ref('')
  const statusText = ref('')

  const selectedRadius = ref(5000)
  const selectedCategory = ref('all')
  const lastCenter = ref(DEFAULT_CENTER)

  const initMap = async () => {
    const amapKey = import.meta.env.VITE_AMAP_KEY
    const amapSecurityCode = import.meta.env.VITE_AMAP_SECURITY_CODE
    await loadAmap(amapKey, amapSecurityCode)
    if (!mapContainer.value) return
    map.value = createMap(mapContainer.value, DEFAULT_CENTER)
    placeSearch.value = createPlaceSearch()
    amapReady.value = true
  }

  const searchNearby = async (center) => {
    if (!placeSearch.value || !map.value) return

    const keywords = CATEGORY_KEYWORDS[selectedCategory.value] || CATEGORY_KEYWORDS.all
    const radius = selectedRadius.value || 5000
    statusText.value = `正在检索（半径 ${(radius / 1000).toFixed(0)}km）...`

    let merged = []
    for (const keyword of keywords) {
      const result = await searchNearBy(placeSearch.value, keyword, center, radius)
      merged = merged.concat(result)
      if (merged.length >= 8) break
    }

    if (merged.length < 3) {
      const expandedRadius = Math.min(radius * 2, 20000)
      for (const keyword of FALLBACK_KEYWORDS) {
        const result = await searchNearBy(placeSearch.value, keyword, center, expandedRadius)
        merged = merged.concat(result)
        if (merged.length >= 12) break
      }
    }

    pois.value = dedupePois(merged)
    selectedPoi.value = null
    selectedPoiKey.value = null
    selectedPoiDetails.value = null
    detailsLoading.value = false
    poiMarkers.value = new Map()
    map.value.clearMap()

    if (pois.value.length === 0) {
      statusText.value = '检索完成：未找到匹配回收点'
      if (currentCenterMarker.value) {
        map.value.add(currentCenterMarker.value)
      }
      return
    }

    statusText.value = `检索完成：找到 ${pois.value.length} 个回收点`
    const markers = []
    pois.value.forEach((poi, index) => {
      if (!poi.location) return
      const marker = makeMarker(poi.location, poi.name, index + 1, 'green')
      const key = poi.id || `${poi.name || ''}_${poi.address || ''}`
      marker.on('click', () => {
        selectPoiByKey(key)
      })
      poiMarkers.value.set(key, marker)
      markers.push(marker)
    })
    if (currentCenterMarker.value) {
      markers.push(currentCenterMarker.value)
    }
    if (markers.length > 0) {
      map.value.add(markers)
      map.value.setFitView(markers)
    }

    if (pois.value.length > 0) {
      selectPoi(pois.value[0], false)
    }
  }

  const selectPoiByKey = (key) => {
    const poi = pois.value.find((item) => (item.id || `${item.name || ''}_${item.address || ''}`) === key)
    if (poi) {
      selectPoi(poi, true)
    }
  }

  const loadSelectedPoiDetails = async (poi, key) => {
    selectedPoiDetails.value = null
    if (!poi?.id) {
      return
    }

    detailsLoading.value = true
    try {
      const details = await getPlaceDetails(placeSearch.value, poi.id)
      // Ignore outdated async response.
      if (selectedPoiKey.value !== key) return
      selectedPoiDetails.value = details ? { ...poi, ...details } : null
    } finally {
      if (selectedPoiKey.value === key) {
        detailsLoading.value = false
      }
    }
  }

  const selectPoi = (poi, panTo = true) => {
    if (!poi) return
    const key = poi.id || `${poi.name || ''}_${poi.address || ''}`
    selectedPoi.value = poi
    selectedPoiKey.value = key
    detailsLoading.value = false
    void loadSelectedPoiDetails(poi, key)

    poiMarkers.value.forEach((marker) => {
      setMarkerTheme(marker, 'green')
    })

    const selectedMarker = poiMarkers.value.get(key)
    if (selectedMarker) {
      setMarkerTheme(selectedMarker, 'highlight')
      if (panTo && map.value) {
        const position = selectedMarker.getPosition()
        if (position) {
          map.value.panTo(position)
        }
      }
    }
  }

  const locateAndSearch = () => {
    if (!amapReady.value) return
    isLoading.value = true
    errorMessage.value = ''
    statusText.value = ''

    const runWithCenter = (center, markerTitle) => {
      lastCenter.value = center
      map.value.setCenter(center)
      currentCenterMarker.value = makeMarker(center, markerTitle, null, 'blue-default')
      map.value.add(currentCenterMarker.value)
      return searchNearby(center).finally(() => {
        isLoading.value = false
      })
    }

    if (!navigator.geolocation) {
      errorMessage.value = '当前浏览器不支持定位，已使用默认位置。'
      runWithCenter(DEFAULT_CENTER, '当前位置（默认）')
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        runWithCenter([position.coords.longitude, position.coords.latitude], '当前位置')
      },
      () => {
        errorMessage.value = '定位失败，已使用默认位置。建议开启浏览器定位权限后重试。'
        runWithCenter(DEFAULT_CENTER, '当前位置（默认）')
      },
      {
        enableHighAccuracy: true,
        timeout: 8000
      }
    )
  }

  const searchWithCurrentSettings = () => {
    if (!amapReady.value || isLoading.value) return
    isLoading.value = true
    searchNearby(lastCenter.value).finally(() => {
      isLoading.value = false
    })
  }

  const destroyMap = () => {
    if (map.value) {
      map.value.destroy()
      map.value = null
    }
  }

  const formatDistance = (distance) => {
    if (distance === undefined || distance === null) return '未知'
    if (distance < 1000) return `${distance} 米`
    return `${(distance / 1000).toFixed(2)} 公里`
  }

  return {
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
  }
}
