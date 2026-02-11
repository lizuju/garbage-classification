export const DEFAULT_CENTER = [116.397428, 39.90923]

export const RADIUS_OPTIONS = [
  { label: '1km', value: 1000 },
  { label: '3km', value: 3000 },
  { label: '5km', value: 5000 },
  { label: '10km', value: 10000 },
  { label: '15km', value: 15000 }
]

export const CATEGORY_OPTIONS = [
  { label: '全部回收点', value: 'all' },
  { label: '可回收物', value: 'recyclable' },
  { label: '厨余垃圾', value: 'kitchen' },
  { label: '有害垃圾', value: 'hazardous' },
  { label: '其他垃圾', value: 'other' }
]

export const CATEGORY_KEYWORDS = {
  all: [
    '垃圾分类投放点', '回收站', '废品回收站', '再生资源回收', '分类驿站', '回收箱',
    '废纸回收', '废金属回收', '旧货回收',
    '厨余垃圾', '湿垃圾',
    '有害垃圾', '电池回收', '过期药品回收',
    '干垃圾', '生活垃圾收运点'
  ],
  recyclable: ['可回收物回收点', '废品回收站', '再生资源回收', '旧货回收', '废纸回收', '废金属回收'],
  kitchen: ['厨余垃圾投放点', '湿垃圾投放点', '垃圾分类投放点', '有机垃圾'],
  hazardous: ['有害垃圾投放点', '电池回收点', '垃圾分类投放点', '过期药品回收', '灯管回收'],
  other: ['其他垃圾投放点', '干垃圾投放点', '垃圾分类投放点', '生活垃圾收运点']
}

export const FALLBACK_KEYWORDS = [
  '垃圾站', '环卫站', '垃圾分类站', '资源回收', '废旧物资回收', 
  '便民回收点', '垃圾中转站', '环卫设施'
]
