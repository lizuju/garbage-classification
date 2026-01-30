<template>
  <div class="page-hero-section" :class="{ 'hero-compact': compact }">
    <div class="page-hero-content d-flex flex-column align-items-center">
      <img 
        v-reveal
        v-if="icon"
        :src="icon" 
        alt="Page Icon" 
        class="page-hero-icon hero-fade-in anim-delay-1"
      />
      
      <h1 v-reveal class="page-hero-title text-center hero-fade-in anim-delay-2">{{ title }}</h1>
      
      <p v-reveal v-if="subtitle" class="page-hero-subtitle text-center hero-fade-in anim-delay-3">{{ subtitle }}</p>
      
      <div v-reveal v-if="ctaText && ctaLink" class="hero-fade-in">
        <CommonButton
          :href="ctaLink"
          theme="secondary"
          size="lg"
          @click="handleCtaClick"
        >
          <i class="bi bi-arrow-down-circle me-2"></i>
          {{ ctaText }}
        </CommonButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import CommonButton from '@/components/CommonButton.vue';
import iconPlaceholder from '@/assets/icons/apple-touch-icon.png';

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: iconPlaceholder
  },
  ctaText: {
    type: String,
    default: ''
  },
  ctaLink: {
    type: String,
    default: ''
  },
  compact: {
    type: Boolean,
    default: false
  }
});
</script>

<style scoped>
.page-hero-section {
  width: 100%;
  min-height: 81vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.hero-compact {
  min-height: 40vh; /* Reduced height for functional pages */
}

.page-hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 4rem 2rem;
}

/* Hero Icon */
.page-hero-icon {
  width: 140px;
  height: 140px;
  margin-bottom: 40px;
  border-radius: 40px;
}

.hero-compact .page-hero-icon {
  width: 100px;
  height: 100px;
  margin-bottom: 25px;
}

/* Hero Title - dark text for white background */
.page-hero-title {
  font-size: 3.8rem;
  font-weight: 800;
  letter-spacing: -1px;
  margin-bottom: 24px;
  display: block;
  color: #1d1d1f !important;
  text-shadow: none !important;
}

.hero-compact .page-hero-title {
  font-size: 2.8rem;
  margin-bottom: 16px;
}

/* Hero Subtitle - dark text for white background */
.page-hero-subtitle {
  font-size: 1.8rem;
  font-weight: 300;
  letter-spacing: 4px;
  margin-bottom: 40px;
  color: #333 !important;
  text-shadow: none !important;
}

.hero-compact .page-hero-subtitle {
  font-size: 1.4rem;
  letter-spacing: 2px;
}

/* Responsive */
@media (max-width: 768px) {
  .page-hero-section {
    min-height: 60vh;
  }
  
  .hero-compact {
    min-height: 30vh;
  }

  .page-hero-icon {
    width: 100px;
    height: 100px;
  }
  
  .hero-compact .page-hero-icon {
    width: 80px;
    height: 80px;
  }

  .page-hero-title {
    font-size: 2.5rem;
  }
  
  .hero-compact .page-hero-title {
    font-size: 2rem;
  }

  .page-hero-subtitle {
    font-size: 1.2rem;
    letter-spacing: 2px;
  }
}
</style>
