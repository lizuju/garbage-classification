<template>
  <div class="about-page-wrapper">
    <!-- Hero Section -->
    <PageHero
      title="关于项目"
      subtitle="基于YOLOv5的垃圾分类识别系统"
      ctaText="开始了解"
      ctaLink="#project-overview"
    />

    <!-- Main Content -->
    <div class="about-content">
        <!-- 项目概述 -->
        <h2 v-reveal id="project-overview" class="section-title hero-fade-in anim-delay-1">项目概述</h2>
        <div class="about-guide-card overview-card">
          <div class="about-card-content overview-split">
            <div class="overview-image">
              <img src="@/assets/about-card-overview.jpg" alt="垃圾分类系统演示" />
            </div>
            <div class="overview-text">
              <p>
                本系统基于先进的深度学习技术，采用 YOLOv5 目标识别模型，实现对垃圾的自动识别与智能分类。用户只需上传一张图片，系统即可在瞬间完成分析，精准判断垃圾类别，为正确分类提供直观、可靠的指引。通过技术赋能日常行为，让环保变得更简单、更高效。
              </p>
            </div>
          </div>
        </div>

        <!-- 主要功能 -->
        <h2 v-reveal class="section-title hero-fade-in anim-delay-1">主要功能</h2>
        <div class="about-guide-card features-card">
          <div class="about-card-content features-split">
            <div class="features-text">
              <p>
                系统支持图片上传与实时预览，所见即所得。通过 AI 智能识别引擎，对垃圾进行快速检测与精准分类，让判断更高效、更可靠。所有识别记录都会被自动保存，方便用户随时回溯与管理。同时，系统提供完善的用户管理与权限控制机制，并在管理后台中以数据化方式呈现统计与分析结果，为运营与决策提供清晰依据。
              </p>
            </div>
            <div class="features-image">
              <img src="@/assets/about-card-feature.jpg" alt="主要功能展示" />
            </div>
          </div>
        </div>

        <!-- 技术架构 -->
        <h2 v-reveal class="section-title hero-fade-in anim-delay-1">技术架构</h2>
        <div class="about-guide-card tech-card">
          <div class="about-card-content tech-split">
            <div class="tech-image">
              <img src="@/assets/about-card-tech.jpg" alt="技术栈展示" />
            </div>
            <div class="tech-text">
              <p>
                系统采用现代化的全栈技术架构构建。后端基于 Flask 框架，结合 SQLAlchemy 数据管理与 YOLOv5 目标识别模型，确保服务稳定与识别高效。前端使用 Vue 3 与 Vite 打造流畅、响应迅速的交互体验，并配合 Bootstrap 5 实现简洁统一的界面设计。数据层采用轻量级 SQLite 数据库，支持快速部署，并可灵活运行于本地或云端服务器环境。
              </p>
            </div>
          </div>
        </div>

        <!-- 分类体系 -->
        <h2 v-reveal class="section-title hero-fade-in anim-delay-1">分类体系</h2>
        
        <div class="row g-4">
          <!-- 可回收物 -->
          <div class="col-lg-6">
            <div class="guide-card recyclable">
              <div class="guide-header d-flex justify-content-center align-items-center">
                <i class="bi bi-recycle" style="font-size: 30px;"></i>
                <h5>可回收物</h5>
              </div>
              <div class="guide-content">
                  <p class="main-desc">
                      涵盖生活中具有再生价值的<strong>纸类、塑料、玻璃、金属及纺织品</strong>。这些物品通过循环再生系统，可重新转化为生产原料，是实现绿色可持续发展的核心资源。
                  </p>
                  <div class="example-section">
                      <div class="example-title">
                      <i class="bi bi-lightbulb-fill"></i> 常见回收示例
                      </div>
                      
                      <div class="example-row">
                      <span class="category-label">纸类</span>
                      <span class="item-tags">报纸、书籍、纸板箱</span>
                      </div>
                      <div class="example-row">
                      <span class="category-label">塑料</span>
                      <span class="item-tags">塑料瓶、包装袋、泡沫</span>
                      </div>
                      <div class="example-row">
                      <span class="category-label">玻璃</span>
                      <span class="item-tags">玻璃瓶、镜子、碎玻璃</span>
                      </div>
                      <div class="example-row">
                      <span class="category-label">金属</span>
                      <span class="item-tags">易拉罐、铁罐、钥匙</span>
                      </div>
              </div>
              </div>
            </div>
          </div>

          <!-- 有害垃圾 -->
          <div class="col-lg-6">
          <div class="guide-card harmful">
              <div class="guide-header d-flex justify-content-center align-items-center">
              <i class="bi bi-radioactive" style="font-size: 30px;"></i>
              <h5>有害垃圾</h5>
              </div>
              <div class="guide-content">
              <p class="main-desc">
                  指对人体健康或自然环境造成<strong>直接或潜在危害</strong>的生活废弃物。此类物品必须经过特殊安全处理，严禁随意丢弃，以防止重金属或有毒物质渗入土壤与水源。
              </p>

              <div class="example-section">
                  <div class="example-title">
                  <i class="bi bi-shield-exclamation"></i> 严禁混放示例
                  </div>
                  
                  <div class="example-row">
                  <span class="category-label">电池</span>
                  <span class="item-tags">纽扣电池、充电电池、铅蓄电池</span>
                  </div>
                  <div class="example-row">
                  <span class="category-label">灯管</span>
                  <span class="item-tags">荧光灯管、节能灯、紫外线灯</span>
                  </div>
                  <div class="example-row">
                  <span class="category-label">医药</span>
                  <span class="item-tags">过期药品、药水瓶、水银温度计</span>
                  </div>
                  <div class="example-row">
                  <span class="category-label">化工</span>
                  <span class="item-tags">废油漆桶、杀虫剂、矿物油</span>
                  </div>
              </div>
              </div>
          </div>
          </div>

          <!-- 厨余垃圾 -->
          <div class="col-lg-6">
          <div class="guide-card kitchen">
              <div class="guide-header d-flex justify-content-center align-items-center">
              <i class="bi bi-egg-fried" style="font-size: 30px;"></i>
              <h5>厨余垃圾</h5>
              </div>
              <div class="guide-content">
              <p class="main-desc">
                  指居民日常生活及食品加工中产生的<strong>易腐烂生物质</strong>废弃物。通过生物技术处理，这些垃圾可转化为高品质的有机肥料或生物油脂，实现大自然循环。
              </p>

              <div class="example-section">
                  <div class="example-title">
                  <i class="bi bi-moisture"></i> 易腐物投放示例
                  </div>
                  
                  <div class="example-row">
                  <span class="category-label">熟食</span>
                  <span class="item-tags">剩菜剩饭、餐后汤渣、过期零食</span>
                  </div>
                  <div class="example-row">
                  <span class="category-label">食材</span>
                  <span class="item-tags">菜根菜叶、肉类残渣、水产内脏</span>
                  </div>
                  <div class="example-row">
                  <span class="category-label">果壳</span>
                  <span class="item-tags">瓜果皮核、碎蛋壳、茶叶渣、咖啡渣</span>
                  </div>
                  <div class="example-row">
                  <span class="category-label">骨骼</span>
                  <span class="item-tags">鱼骨、鸡鸭骨头（大骨头建议投至其他垃圾）</span>
                  </div>
              </div>
              </div>
          </div>
          </div>

          <!-- 其他垃圾 -->
          <div class="col-lg-6">
          <div class="guide-card other">
              <div class="guide-header d-flex justify-content-center align-items-center">
              <i class="bi bi-trash" style="font-size: 30px;"></i>
              <h5>其他垃圾</h5>
              </div>
              <div class="guide-content">
              <p class="main-desc">
                  指除可回收物、有害垃圾、厨余垃圾以外的<strong>其他生活废弃物</strong>。此类垃圾通常采取卫生填埋或焚烧发电等方式处理，能有效减少环境污染并转化部分能源。
              </p>

              <div class="example-section">
                  <div class="example-title">
                  <i class="bi bi-info-circle-fill"></i> 常见其他垃圾示例
                  </div>
                  
                  <div class="example-row">
                  <span class="category-label">卫生</span>
                  <span class="item-tags">卫生纸、湿巾、一次性餐具</span>
                  </div>
                  <div class="example-row">
                  <span class="category-label">复合</span>
                  <span class="item-tags">大骨头、硬贝壳、椰子壳</span>
                  </div>
                  <div class="example-row">
                  <span class="category-label">顽固</span>
                  <span class="item-tags">烟蒂、尘土、破旧陶瓷</span>
                  </div>
                  <div class="example-row">
                  <span class="category-label">其他</span>
                  <span class="item-tags">宠物粪便、不可降解塑料袋</span>
                  </div>
              </div>
              </div>
          </div>
          </div>
        </div>

        <!-- 联系我们 -->
        <h2 v-reveal class="section-title hero-fade-in anim-delay-1">联系我们</h2>
        <div v-reveal class="contact-important-card hero-fade-in">
          <h3 class="contact-card-title">
            <i class="bi bi-chat-dots-fill text-danger me-2"></i>如有问题或建议，欢迎联系
          </h3>
          
          <div class="row g-5 justify-content-center">
            <!-- Email -->
            <div v-reveal class="col-6 hero-fade-in anim-delay-1">
              <div class="contact-item">
                <div class="contact-icon-box bg-white">
                  <i class="bi bi-envelope-fill text-primary"></i>
                </div>
                <h6>Email</h6>
                <p>li2096870763@gmail.com</p>
              </div>
            </div>

            <!-- Phone -->
            <div v-reveal class="col-6 hero-fade-in anim-delay-2">
              <div class="contact-item">
                <div class="contact-icon-box bg-white">
                  <i class="bi bi-telephone-fill text-success"></i>
                </div>
                <h6>Phone</h6>
                <p>+86 132 5054 1959</p>
              </div>
            </div>
          </div>

          <!-- Toggle Button -->
          <div v-reveal class="hero-fade-in d-flex justify-content-center mt-5">
            <CommonButton 
              @click="toggleContact" 
              theme="gold"
              size="md"
            >
              {{ isContactExpanded ? '取消联系' : '立即联系' }}
            </CommonButton>
          </div>

          <!-- Expandable Image Section -->
          <transition name="expand">
            <div v-if="isContactExpanded" class="contact-expand-section mt-4 text-center">
              <div class="qr-container">
                <img src="@/assets/qr-code.jpg" alt="Contact QR Code" class="contact-qr-img" />
              </div>
            </div>
          </transition>
        </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import CommonButton from '@/components/CommonButton.vue';
import PageHero from '@/components/PageHero.vue';
import '../styles/pages/about.css';
import '../styles/components/entrance-reveal.css';

// Contact expansion state
const isContactExpanded = ref(false);

const toggleContact = () => {
  isContactExpanded.value = !isContactExpanded.value;
};
</script>