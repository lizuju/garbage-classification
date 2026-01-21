<template>
  <a
    v-if="href"
    :href="href"
    :class="['base-custom-btn', `btn-${theme}`, `btn-${size}`]"
    @click="$emit('click', $event)"
  >
    <slot></slot>
  </a>
  <router-link
    v-else-if="to"
    :to="to"
    :class="['base-custom-btn', `btn-${theme}`, `btn-${size}`]"
  >
    <slot></slot>
  </router-link>
  
  <button
    v-else
    :type="nativeType"
    :class="['base-custom-btn', `btn-${theme}`, `btn-${size}`]"
    @click="$emit('click')"
  >
    <slot></slot>
  </button>
</template>

<script setup>
defineProps({
  href: { 
    type: String, 
    default: null 
  },
  // 跳转路径，如果不传则渲染为普通 button
  to: {
    type: [String, Object],
    default: null
  },
  // 主题颜色：success, info, primary
  theme: {
    type: String,
    default: 'success'
  },
  // 尺寸：sm, md, lg
  size: {
    type: String,
    default: 'lg'
  },
  // 原生按钮类型
  nativeType: {
    type: String,
    default: 'button'
  }
});

defineEmits(['click']);
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

/* --- 图标移动逻辑 --- */
/* 使用 :deep() 确保样式能作用到通过 <slot> 传入的图标上 */
:deep(.icon-move) {
  display: inline-block;
  transition: transform 0.3s ease;
}

/* 鼠标移入整个按钮时，内部带有 .icon-move 类的图标向右移动 4px */
.base-custom-btn:hover :deep(.icon-move) {
  transform: translateX(4px);
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
.base-custom-btn:hover {
  transform: translateY(-5px) scale(1.03);
  background-position: right center;
}

.base-custom-btn:hover::after {
  left: 100%;
  transition: all 0.7s ease;
}

/* 激活反馈 */
.base-custom-btn:active {
  transform: translateY(2px) scale(0.92);
  transition: transform 0.1s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 颜色主题配置 */
/* --- 调优后的深色系微渐变配色 --- */

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

/* 内部图标过渡效果 */
:deep(.icon-move) {
  display: inline-block;
  transition: transform 0.3s ease;
}
.base-custom-btn:hover :deep(.icon-move) {
  transform: translateX(3px);
}
</style>