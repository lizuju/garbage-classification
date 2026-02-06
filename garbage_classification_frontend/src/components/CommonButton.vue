<template>
  <!-- 普通 a 标签或者 hash -->
  <a
    v-if="href"
    :href="href"
    :class="['base-custom-btn', `btn-${theme}`, `btn-${size}`, { 'btn-circle': circle }]"
    @click.prevent="handleClick"
  >
    <slot></slot>
  </a>

  <!-- router-link 跨页面 -->
  <router-link
    v-else-if="to"
    :to="to"
    :class="['base-custom-btn', `btn-${theme}`, `btn-${size}`, { 'btn-circle': circle }]"
    @click.native="handleRouterClick"
  >
    <slot></slot>
  </router-link>

  <!-- 普通按钮 -->
  <button
    v-else
    :type="nativeType"
    :class="['base-custom-btn', `btn-${theme}`, `btn-${size}`, { 'btn-circle': circle }]"
    @click="emitClick"
  >
    <slot></slot>
  </button>
</template>

<script setup>
import { nextTick } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  href: { type: String, default: null }, // 内部 hash 或外部链接
  to: { type: [String, Object], default: null }, // 跨页面跳转
  theme: { type: String, default: 'success' },
  size: { type: String, default: 'lg' },
  nativeType: { type: String, default: 'button' },
  circle: { type: Boolean, default: false }
})

const emit = defineEmits(['click'])
const router = useRouter()

// 普通按钮点击
const emitClick = (event) => {
  emit('click', event)
}

// a 标签点击
const handleClick = (event) => {
  emit('click', event)

  // 内部 hash 滚动
  if (props.href && props.href.startsWith('#')) {
    const el = document.querySelector(props.href)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
    }
  }
}

// router-link 跨页面 hash
const handleRouterClick = async (event) => {
  emit('click', event)

  if (typeof props.to === 'string' && props.to.includes('#')) {
    const hash = props.to.split('#')[1]

    await nextTick() // 等 DOM 渲染

    const el = document.getElementById(hash)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
    }
  }
}
</script>