export const loadAmap = async (key, securityCode) => {
  if (!key) {
    throw new Error('缺少 VITE_AMAP_KEY，请在前端环境变量中配置高德 Key')
  }

  if (window.AMap) return

  if (securityCode) {
    window._AMapSecurityConfig = {
      securityJsCode: securityCode
    }
  }

  await new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${key}&plugin=AMap.PlaceSearch`
    script.async = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('高德地图脚本加载失败'))
    document.head.appendChild(script)
  })
}

export const createMap = (container, center = [116.397428, 39.90923]) => {
  return new window.AMap.Map(container, {
    zoom: 13,
    center
  })
}

export const createPlaceSearch = () => {
  return new window.AMap.PlaceSearch({
    pageSize: 20,
    pageIndex: 1,
    extensions: 'all'
  })
}

export const searchNearBy = (placeSearch, keyword, center, radius) => {
  return new Promise((resolve) => {
    if (!placeSearch) {
      resolve([])
      return
    }
    placeSearch.searchNearBy(keyword, center, radius, (status, result) => {
      if (status !== 'complete' || !result?.poiList?.pois) {
        resolve([])
        return
      }
      resolve(result.poiList.pois)
    })
  })
}

export const getPlaceDetails = (placeSearch, poiId) => {
  return new Promise((resolve) => {
    if (!placeSearch || !poiId) {
      resolve(null)
      return
    }
    placeSearch.getDetails(poiId, (status, result) => {
      if (status !== 'complete') {
        resolve(null)
        return
      }

      const fromPoi = result?.poiList?.pois?.[0] || null
      const fromInfo = result?.poi || null
      resolve(fromPoi || fromInfo || null)
    })
  })
}

export const makeMarker = (position, title, labelText = null, theme = 'green') => {
  // For "my location", use AMap default marker style (blue) plus top label.
  if (theme === 'blue-default') {
    const options = {
      position,
      title,
      icon: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png'
    }
    if (labelText !== null) {
      options.label = {
        content: String(labelText),
        direction: 'top'
      }
    }
    return new window.AMap.Marker(options)
  }

  const colors = {
    green: '#16a34a',
    blue: '#2563eb',
    highlight: '#f59e0b'
  }
  const markerColor = colors[theme] || colors.green

  const markerContent = document.createElement('div')
  markerContent.style.minWidth = '26px'
  markerContent.style.height = '26px'
  markerContent.style.padding = labelText ? '0 8px' : '0'
  markerContent.style.borderRadius = '14px'
  markerContent.style.background = markerColor
  markerContent.style.color = '#fff'
  markerContent.style.fontSize = '12px'
  markerContent.style.fontWeight = '700'
  markerContent.style.display = 'flex'
  markerContent.style.alignItems = 'center'
  markerContent.style.justifyContent = 'center'
  markerContent.style.boxShadow = '0 2px 8px rgba(0,0,0,0.25)'
  markerContent.style.border = '2px solid #ffffff'
  markerContent.style.whiteSpace = 'nowrap'
  markerContent.textContent = labelText ? String(labelText) : ''

  const markerOptions = {
    position,
    title,
    content: markerContent
  }
  const marker = new window.AMap.Marker(markerOptions)
  marker.setExtData({
    labelText,
    theme
  })
  return marker
}

export const setMarkerTheme = (marker, theme = 'green') => {
  if (!marker) return
  const ext = marker.getExtData ? marker.getExtData() : {}
  const labelText = ext?.labelText ?? null
  const title = marker.getTitle ? marker.getTitle() : ''
  const position = marker.getPosition ? marker.getPosition() : null
  if (!position) return
  const updated = makeMarker(position, title, labelText, theme)
  marker.setContent(updated.getContent())
  marker.setExtData({
    ...ext,
    theme
  })
  if (theme === 'highlight') {
    marker.setzIndex(130)
  } else {
    marker.setzIndex(120)
  }
}

export const dedupePois = (poiList) => {
  const byKey = new Map()
  poiList.forEach((poi) => {
    const key = poi.id || `${poi.name || ''}_${poi.address || ''}`
    if (!byKey.has(key)) byKey.set(key, poi)
  })
  return Array.from(byKey.values())
}
