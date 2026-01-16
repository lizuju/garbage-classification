<template>
  <component :is="layout">
    <slot />
  </component>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './Navbar.vue'
import Footer from './Footer.vue'

const route = useRoute()

// 某些页面不显示 Navbar/Footer
const isFullScreen = computed(() => {
  return route.meta.fullScreen || false
})

// 动态选择布局
const layout = computed(() => {
  if (isFullScreen.value) {
    return 'div'
  }
  return 'div'
})
</script>
