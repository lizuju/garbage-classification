<template>
  <!-- 普通 a 标签或者 hash -->
  <a
    v-if="href"
    :href="href"
    :class="['base-custom-btn', `btn-${theme}`, `btn-${size}`]"
    @click.prevent="handleClick"
  >
    <slot></slot>
  </a>

  <!-- router-link 跨页面 -->
  <router-link
    v-else-if="to"
    :to="to"
    :class="['base-custom-btn', `btn-${theme}`, `btn-${size}`]"
    @click.native="handleRouterClick"
  >
    <slot></slot>
  </router-link>

  <!-- 普通按钮 -->
  <button
    v-else
    :type="nativeType"
    :class="['base-custom-btn', `btn-${theme}`, `btn-${size}`]"
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
  nativeType: { type: String, default: 'button' }
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

<style scoped>
/* 核心：抽象出来的基础按钮样式 */
.base-custom-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  border: none;
  border-radius: 50px;
  overflow: hidden;
  color: #ffffff !important;
  font-weight: 600;
  cursor: pointer;
  z-index: 1;
  background-size: 200% auto;
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  text-shadow: 0 1px 2px rgba(0,0,0,0.15); /* 给文字一点点阴影，让它从深色背景中浮出来 */
  letter-spacing: 0.2px; /* 增加一点点字间距，显得更精致 */
}

/* 尺寸定义 */
.btn-lg { padding: 18px 50px; font-size: 1.25rem; }
.btn-md { padding: 12px 35px; font-size: 1.05rem; }
.btn-sm { padding: 8px 20px; font-size: 0.9rem; }

/* 高级感核心：掠过的一道光影 (保留所有原生效果) */
.base-custom-btn::after {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.4) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  transition: none;
  z-index: -1;
}

/* 悬停状态 */
.base-custom-btn:not(:disabled):hover {
  transform: translateY(-5px) scale(1.03);
  background-position: right center;
}

.base-custom-btn:not(:disabled):hover::after {
  left: 100%;
  transition: all 0.7s ease;
}

/* 激活反馈 */
.base-custom-btn:active {
  transform: translateY(2px) scale(0.92);
  transition: transform 0.1s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 增加禁用状态的视觉反馈 */
.base-custom-btn:disabled,
.base-custom-btn[disabled] {
  cursor: not-allowed;
  filter: grayscale(0.6); /* 变灰色 */
  opacity: 0.7;
  transform: none !important; /* 禁用缩放动画 */
  box-shadow: none !important; /* 移除阴影 */
}

/* 内部图标过渡效果 */
/* 自动识别 slot 里的图标(i)或文字(span)并使其移动 */
.base-custom-btn:hover:not(:disabled) :deep(i),
.base-custom-btn:hover:not(:disabled) :deep(span),
.base-custom-btn:hover:not(:disabled) :deep(.bi) { /* 针对 Bootstrap Icons 的类名 */
  display: inline-block; /* 必须确保是 inline-block 才能应用 transform */
  transform: translateX(4px);
  transition: transform 0.3s ease;
}
/* 默认状态下的过渡效果（防止移动时闪现/生硬） */
:deep(i), :deep(span), :deep(.bi) {
  transition: transform 0.3s ease;
}

/* 颜色主题配置 */
/* 1. 成功绿 (森林翠绿：更深邃，带微妙明暗差) */
.btn-success {
  background: linear-gradient(180deg, #16a34a 0%, #15803d 100%);
  box-shadow: 0 4px 14px 0 rgba(22, 163, 74, 0.3);
}
.btn-success:hover {
  background: linear-gradient(180deg, #15803d 0%, #166534 100%);
  box-shadow: 0 6px 20px rgba(22, 163, 74, 0.4);
}

/* 2. 信息蓝 (调淡版：通透的湖蓝色渐变) */
.btn-info {
  /* 调淡了起始色，增加了呼吸感 */
  background: linear-gradient(180deg, #38bdf8 0%, #0ea5e9 100%); 
  box-shadow: 0 4px 14px rgba(56, 189, 248, 0.3);
}
.btn-info:hover {
  background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 100%);
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.4);
}

/* 3. 主题蓝 (深邃交互蓝：比之前的黑色更有科技感) */
.btn-primary {
  background: linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%);
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
}
.btn-primary:hover {
  background: linear-gradient(180deg, #2563eb 0%, #1e40af 100%);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
}

/* 4. 金色主题 (流动金属质感) */
.btn-gold {
  background: linear-gradient(180deg, #fff4d6 0%, #d4c391 100%);
  box-shadow: 0 4px 14px rgba(183, 140, 31, 0.3);
}
.btn-gold:hover {
  background: linear-gradient(180deg, #fff8e6 0%, #dbc88f 100%);
  box-shadow: 0 6px 20px rgba(184, 134, 11, 0.4);
}

/* 额外增加一个：半透明毛玻璃质感 (如果背景很复杂时使用) */
.btn-glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff !important;
  box-shadow: 0 4px 14px 0 rgba(0, 0, 0, 0.1);
}
.btn-glass:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>