<template>
  <div class="home-page">
    <!-- 英雄 Header -->
    <div class="hero-section">
      <div class="hero-content d-flex flex-column align-items-center">
        <h1 v-reveal class="hero-title text-center hero-fade-in anim-delay-2">🗑️ 基于YOLOv5的垃圾分类识别系统</h1>
        <p v-reveal class="hero-subtitle text-center hero-fade-in anim-delay-3">上传图片，AI 帮您快速识别垃圾类别</p>
        <p v-reveal class="hero-description text-center hero-fade-in anim-delay-4">使用深度学习和计算机视觉技术，让垃圾分类变得简单高效</p>
        <div v-reveal class="hero-fade-in">
          <CommonButton
            @click="handleStart"
            theme="success"
            size="lg"
          >
            <i class="bi bi-play-circle me-2"></i>
            {{ isLoggedIn ? '立即开始识别' : '登录开始使用' }}
          </CommonButton>
        </div>
      </div>
    </div>

    <!-- 主内容 -->
    <div class="home-content-wrapper">

      <!-- 功能模块区 - 3 列并排 -->
      <div class="feature-scroll-section">
        <h1 v-reveal class="section-title hero-fade-in anim-delay-1">探索更多功能</h1>
        
        <div class="feature-scroll-container">
          <div class="feature-item">
            <div class="card feature-card card-bg-1"> <div class="card-overlay"></div>
              <div class="card-body d-flex flex-column justify-content-center align-items-center p-5">
                <div class="icon-box mb-4">
                  <i class="bi bi-clock-history feature-icon text-info"></i>
                </div>
                <h3 class="feature-description">
                  每一次识别都会被自动保存，<br>
                  清晰呈现您的环保足迹，<br>
                  让改变看得见。
                </h3>
                <common-button
                  @click="handleHistory"
                  theme="info"
                  size="md"
                >
                  {{ isLoggedIn ? '立即进入历史' : '登录查看历史' }}
                </common-button>
              </div>
            </div>
          </div>

          <div class="feature-item">
            <div class="card feature-card card-bg-2"> <div class="card-overlay"></div>
              <div class="card-body d-flex flex-column justify-content-center align-items-center p-5">
                <div class="icon-box mb-4">
                  <i class="bi bi-book feature-icon text-success"></i>
                </div>
                <h3 class="feature-description">
                  覆盖全面的分类百科，<br>
                  快速找到每一件物品的正确去向，<br>
                  简单而准确。
                </h3>
                <common-button
                  :href="'#classification-guide'"
                  theme="success"
                  size="md"
                  @click="handleHashClick"
                >
                  了解分类指南
                </common-button>
              </div>
            </div>
          </div>

          <div class="feature-item">
            <div class="card feature-card card-bg-3"> <div class="card-overlay"></div>
              <div class="card-body d-flex flex-column justify-content-center align-items-center p-5">
                <div class="icon-box mb-4">
                  <i class="bi bi-person feature-icon text-primary"></i>
                </div>
                <h3 class="feature-description">
                  根据您的习惯进行个性化设置，<br>
                  统一管理账户信息与安全，<br>
                  一切井然有序。
                </h3>
                <common-button 
                  @click="handleProfile"
                  theme="primary"
                  size="md"
                >
                  {{ isLoggedIn ? '前往个人管理' : '登录管理资料' }}
                </common-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 垃圾分类指南 -->
      <h1 v-reveal id="classification-guide" class="section-title hero-fade-in anim-delay-1">垃圾分类指南</h1>

      <div class="classification-guide">

        <div class="row g-4">
          <!-- 可回收物 -->
          <div class="col-lg-6">
            <div class="guide-card recyclable">
              <div class="guide-header d-flex justify-content-center align-items-center">
                <i class="bi bi-recycle" style="font-size: 30px;"></i>
                <h5>可回收垃圾</h5>
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
                  <span class="category-label">日用</span>
                  <span class="item-tags">受污染纸张、湿纸巾、烟头、灰尘</span>
                  </div>
                  <div class="example-row">
                  <span class="category-label">陶瓷</span>
                  <span class="item-tags">陶瓷碗碟、花盆、损毁瓷砖、镜子</span>
                  </div>
                  <div class="example-row">
                  <span class="category-label">卫浴</span>
                  <span class="item-tags">一次性餐具、卫生巾、尿不湿</span>
                  </div>
                  <div class="example-row">
                  <span class="category-label">杂物</span>
                  <span class="item-tags">贝壳、坚果大壳、枯萎花卉、旧鞋子</span>
                  </div>
              </div>
              </div>
          </div>
          </div>
        </div>
      </div>

      <!-- 为什么分类 -->
      <div v-reveal> <h1 class="section-title hero-fade-in anim-delay-1">重塑循环之美</h1>
        
        <div class="why-important-container">
          <div v-reveal class="why-important-card hero-fade-in">
            <h3 class="why-card-title">
              <i class="bi bi-heart-fill text-danger me-2"></i>为什么要进行垃圾分类？
            </h3>
            
            <div class="row g-5 justify-content-center">
              <div v-reveal class="col-6 hero-fade-in anim-delay-1">
                <div class="why-item">
                  <div class="why-icon-box bg-white">
                    <i class="bi bi-tree-fill text-success"></i>
                  </div>
                  <h6>保护环境</h6>
                  <p>减少环境污染，从源头降低对自然的影响，<br>持续保护地球的生态系统与生物多样性</p>
                </div>
              </div>

              <div v-reveal class="col-6 hero-fade-in anim-delay-2">
                <div class="why-item">
                  <div class="why-icon-box bg-white">
                    <i class="bi bi-arrow-repeat text-primary"></i>
                  </div>
                  <h6>资源利用</h6>
                  <p>提升资源回收效率，让材料得以被再次利用，<br>推动更加可持续的循环体系。</p>
                </div>
              </div>

              <div v-reveal class="col-6 hero-fade-in anim-delay-3">
                <div class="why-item">
                  <div class="why-icon-box bg-white">
                    <i class="bi bi-heart-pulse-fill" style="color: #764ba2"></i>
                  </div>
                  <h6>健康生活</h6>
                  <p>减少有害物质接触，为家庭营造更安全的生活环境，<br>守护每一位家人的健康。</p>
                </div>
              </div>

              <div v-reveal class="col-6 hero-fade-in anim-delay-4">
                <div class="why-item">
                  <div class="why-icon-box bg-white">
                    <i class="bi bi-globe text-warning"></i>
                  </div>
                  <h6>可持续发展</h6>
                  <p>为子孙后代留下更洁净的环境与更稳定的未来，<br>共同创造一个更加美好的世界。</p>
                </div>
              </div>
              
              <div v-reveal class="hero-fade-in d-flex justify-content-center mt-5">
              <common-button
                  to="/about#about-project"
                  theme="gold"
                  size="md"
                >
                  关于我们
                </common-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useAuthModal } from '@/composables/useAuthModal' // Import useAuthModal
import CommonButton from '@/components/CommonButton.vue';
import '../styles/pages/home.css';

const router = useRouter()
const { isLoggedIn } = useAuth()
// Destructure openLogin and openProfile from useAuthModal
const { openLogin, openProfile } = useAuthModal() 

const handleStart = () => {
  if (isLoggedIn.value) {
    router.push('/user/detect')
  } else {
    // Open login modal instead of redirecting
    openLogin() 
  }
}

const handleHistory = () => {
  if (isLoggedIn.value) {
    router.push('/user/history')
  } else {
    // Open login modal instead of redirecting
    openLogin()
  }
}

const handleProfile = () => {
  if (isLoggedIn.value) {
    // Open profile modal instead of redirecting
    openProfile()
  } else {
    // Open login modal instead of redirecting
    openLogin()
  }
}

const handleHashClick = () => {
  // Logic for hash link if needed, or keep as is in template
}
</script>