<template>
  <!-- 英雄 Header -->
  <div class="hero-section">
    <div class="hero-content d-flex flex-column align-items-center">
      <h1 class="hero-title text-center hero-fade-in anim-delay-1">🗑️ 基于YOLOv5的垃圾分类识别系统</h1>
      <p class="hero-subtitle text-center hero-fade-in anim-delay-2">上传图片，AI 帮您快速识别垃圾类别</p>
      <p class="hero-description text-center hero-fade-in anim-delay-3">使用深度学习和计算机视觉技术，让垃圾分类变得简单高效</p>
      <div class="hero-fade-in anim-delay-4">
        <router-link
          :to="isLoggedIn ? '/user/detect' : '/login'"
          class="btn btn-lg btn-success hero-btn"
        >
          <i class="bi bi-play-circle me-2 icon-move"></i>{{ isLoggedIn ? '立即开始识别' : '登录开始使用' }}
        </router-link>
      </div>
    </div>
  </div>

  <!-- 主内容 -->
  <div class="container-fluid py-5">
    <!-- 识别功能区 - 放大 -->
    <div v-if="false" class="container mb-5">
      <div class="row">
        <div class="col-lg-12">
          <div class="card detection-card shadow-lg">
            <div class="card-body p-5">
              <h2 class="text-center mb-4">
                <i class="bi bi-search me-2"></i>垃圾快速识别
              </h2>
              <div class="row align-items-center">
                <!-- 左侧：演示图 -->
                <div class="col-lg-5 mb-4 mb-lg-0">
                  <img
                    src="https://via.placeholder.com/400x350/667eea/ffffff?text=上传垃圾图片"
                    alt="detection demo"
                    class="img-fluid rounded"
                    style="box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15)"
                  />
                  <p class="text-center text-muted mt-3">上传清晰的垃圾图片以获得最佳识别效果</p>
                </div>

                <!-- 右侧：功能说明 -->
                <div class="col-lg-7">
                  <div class="detection-features">
                    <h5 class="mb-3">
                      <i class="bi bi-lightning-fill text-warning me-2"></i>快速识别
                    </h5>
                    <p class="text-muted">一键上传，瞬间获得识别结果</p>

                    <h5 class="mb-3 mt-4">
                      <i class="bi bi-star-fill text-warning me-2"></i>高精度检测
                    </h5>
                    <p class="text-muted">基于 YOLOv5 模型，支持多物体检测</p>

                    <h5 class="mb-3 mt-4">
                      <i class="bi bi-shield-check me-2 text-success"></i>详细分析
                    </h5>
                    <p class="text-muted">获取每个物体的类别、置信度和位置信息</p>

                    <h5 class="mb-3 mt-4">
                      <i class="bi bi-bookmark-check me-2 text-primary"></i>历史记录
                    </h5>
                    <p class="text-muted">自动保存所有识别记录，随时查看</p>
                  </div>

                  <!-- CTA 按钮 -->
                  <div class="mt-5">
                    <router-link
                      :to="isLoggedIn ? '/user/detect' : '/login'"
                      class="btn btn-primary btn-lg w-100"
                    >
                      <i class="bi bi-upload me-2"></i>{{ isLoggedIn ? '去识别' : '登录后识别' }}
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能模块区 - 3 列并排 -->
    <div class="container mb-5">
      <h3 class="text-center mb-4">探索更多功能</h3>
      <div class="row g-4">
        <!-- 模块 1：查看历史 -->
        <div class="col-lg-4 col-md-6">
          <div class="card feature-card h-100">
            <div class="card-body text-center">
              <i class="bi bi-clock-history feature-icon text-info mb-3"></i>
              <h5 class="card-title">查看历史记录</h5>
              <p class="card-text text-muted">浏览所有识别历史，追踪您的识别成果</p>
              <router-link
                to="/user/history"
                v-if="isLoggedIn"
                class="btn btn-sm btn-info mt-3"
              >
                查看历史
              </router-link>
              <router-link
                to="/login"
                v-else
                class="btn btn-sm btn-info mt-3"
              >
                登录查看
              </router-link>
            </div>
          </div>
        </div>

        <!-- 模块 2：了解指南 -->
        <div class="col-lg-4 col-md-6">
          <div class="card feature-card h-100">
            <div class="card-body text-center">
              <i class="bi bi-book feature-icon text-success mb-3"></i>
              <h5 class="card-title">垃圾分类指南</h5>
              <p class="card-text text-muted">了解四大垃圾分类标准和分类知识</p>
              <a href="#classification-guide" class="btn btn-sm btn-success mt-3">查看指南</a>
            </div>
          </div>
        </div>

        <!-- 模块 3：个人资料 -->
        <div class="col-lg-4 col-md-6">
          <div class="card feature-card h-100">
            <div class="card-body text-center">
              <i class="bi bi-person feature-icon text-primary mb-3"></i>
              <h5 class="card-title">个人资料</h5>
              <p class="card-text text-muted">管理账户信息和系统设置</p>
              <router-link
                to="/user/profile"
                v-if="isLoggedIn"
                class="btn btn-sm btn-primary mt-3"
              >
                前往管理
              </router-link>
              <router-link
                to="/login"
                v-else
                class="btn btn-sm btn-primary mt-3"
              >
                登录管理
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 垃圾分类指南 -->
    <div class="container classification-guide" id="classification-guide">
      <h3 class="text-center mb-5">
        <i class="bi bi-info-circle me-2"></i>垃圾分类知识指南
      </h3>

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
                    <span class="category-label category-label">纸类</span>
                    <span class="item-tags">报纸、书籍、纸板箱</span>
                    </div>
                    <div class="example-row">
                    <span class="category-label category-label">塑料</span>
                    <span class="item-tags">塑料瓶、包装袋、泡沫</span>
                    </div>
                    <div class="example-row">
                    <span class="category-label category-label">玻璃</span>
                    <span class="item-tags">玻璃瓶、镜子、碎玻璃</span>
                    </div>
                    <div class="example-row">
                    <span class="category-label category-label">金属</span>
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
                <span class="category-label category-label">电池</span>
                <span class="item-tags">纽扣电池、充电电池、铅蓄电池</span>
                </div>
                <div class="example-row">
                <span class="category-label category-label">灯管</span>
                <span class="item-tags">荧光灯管、节能灯、紫外线灯</span>
                </div>
                <div class="example-row">
                <span class="category-label category-label">医药</span>
                <span class="item-tags">过期药品、药水瓶、水银温度计</span>
                </div>
                <div class="example-row">
                <span class="category-label category-label">化工</span>
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
                指居民日常生活及食品加工中产生的<strong>易腐烂生物质</strong>废弃物。通过生物技术处理，这些垃圾可转化为高品质的有机肥料或生物油脂，实现从餐桌回馈大地的自然循环。
            </p>

            <div class="example-section">
                <div class="example-title">
                <i class="bi bi-moisture"></i> 易腐物投放示例
                </div>
                
                <div class="example-row">
                <span class="category-label category-label">熟食</span>
                <span class="item-tags">剩菜剩饭、餐后汤渣、过期零食</span>
                </div>
                <div class="example-row">
                <span class="category-label category-label">食材</span>
                <span class="item-tags">菜根菜叶、肉类残渣、水产内脏</span>
                </div>
                <div class="example-row">
                <span class="category-label category-label">果壳</span>
                <span class="item-tags">瓜果皮核、碎蛋壳、茶叶渣、咖啡渣</span>
                </div>
                <div class="example-row">
                <span class="category-label category-label">骨骼</span>
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
                <span class="category-label category-label">日用</span>
                <span class="item-tags">受污染纸张、湿纸巾、烟头、灰尘</span>
                </div>
                <div class="example-row">
                <span class="category-label category-label">陶瓷</span>
                <span class="item-tags">陶瓷碗碟、花盆、损毁瓷砖、镜子</span>
                </div>
                <div class="example-row">
                <span class="category-label category-label">卫浴</span>
                <span class="item-tags">一次性餐具、卫生巾、尿不湿</span>
                </div>
                <div class="example-row">
                <span class="category-label category-label">杂物</span>
                <span class="item-tags">贝壳、坚果大壳、枯萎花卉、旧鞋子</span>
                </div>
            </div>
            </div>
        </div>
        </div>
      </div>
    </div>

    <!-- 为什么分类 -->
    <div class="container mt-5 py-5">
      <div class="row">
        <div class="col-lg-10 offset-lg-1">
          <div class="why-important">
            <h3 class="text-center mb-4">
              <i class="bi bi-heart-fill text-danger me-2"></i>为什么要进行垃圾分类？
            </h3>
            <div class="row g-4">
              <div class="col-md-6">
                <div class="d-flex mb-3">
                  <i class="bi bi-tree-fill text-success me-3" style="font-size: 1.5rem"></i>
                  <div>
                    <h6>保护环境</h6>
                    <p class="text-muted small">减少环境污染，保护生态系统</p>
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="d-flex mb-3">
                  <i class="bi bi-arrow-repeat text-primary me-3" style="font-size: 1.5rem"></i>
                  <div>
                    <h6>资源利用</h6>
                    <p class="text-muted small">提高资源回收率，循环利用</p>
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="d-flex mb-3">
                  <i class="bi bi-health me-3" style="font-size: 1.5rem; color: #764ba2"></i>
                  <div>
                    <h6>健康生活</h6>
                    <p class="text-muted small">减少有害物质接触，保护健康</p>
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="d-flex mb-3">
                  <i class="bi bi-globe me-3" style="font-size: 1.5rem; color: #fd7e14"></i>
                  <div>
                    <h6>可持续发展</h6>
                    <p class="text-muted small">为子孙后代创造美好世界</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuth } from '../composables/useAuth'

const { isLoggedIn } = useAuth()
</script>

<style scoped>
/* 英雄部分 */
.hero-section {
  /* 必须有高度，内容才能撑开背景 */
  /* min-height: 500px; */
  width: 100%;
  height: calc(100vh - 60px);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;                /* 背景变深后，文字通常改为白色 */
  position: relative; /* 必须加这一行，否则伪元素和子元素定位会乱 */
  overflow: hidden;   /* 防止装饰性波浪线溢出 */
  background: #1a1a1a;
}

/* 使用伪元素承载背景图，实现只缩放背景而不影响文字 */
.hero-section::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  
  /* 你的背景图配置 */
  background-color: #1a1a1a;
  background-image: linear-gradient(to right, rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
                    url('../assets/hero-bg.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  
  /* 绑定动画：持续10秒，平滑过渡，无限循环，来回播放 */
  animation: kenburns 10s ease-in-out infinite alternate;
  backface-visibility: hidden;
  transform-style: preserve-3d;
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
}

/* 英雄文字 */
.hero-title {
  font-size: 3.8rem;
  font-weight: 800;
  letter-spacing: -1px;
  margin-bottom: 24px;
  display: block;

  color: #ffffff; 

  text-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.5),      /* 基础投影 */
    0 0 20px rgba(40, 167, 69, 0.2);   /* 微弱的成功绿光晕，呼应你的主题色 */
    
  /* 消除渐变对 Emoji 的影响，确保它们五颜六色 */
  background: none;
  -webkit-background-clip: initial;
  background-clip: initial;
  -webkit-text-fill-color: initial;
}

.hero-subtitle {
  font-size: 1.8rem;
  font-weight: 300; /* 使用细体字增加高级感 */
  letter-spacing: 4px; /* 拉开字间距，显得大气 */
  margin-bottom: 15px;
  color: rgba(255, 255, 255, 0.85);
  text-transform: uppercase; /* 英文如果包含在内会变大写，中文则增加稳重感 */
}

.hero-description {
  font-size: 1.1rem;
  font-weight: 400;
  max-width: 600px;
  line-height: 1.8;
  margin-bottom: 40px;
  color: rgba(255, 255, 255, 0.65);
  border-left: 3px solid #28a745; 
  padding-left: 20px;
  margin-left: auto;
  margin-right: auto;
}

/* 按钮、卡片 */
/* 核心英雄按钮 */
.hero-btn {
  position: relative;
  padding: 18px 50px;
  font-size: 1.25rem;
  color: #fff !important; /* 字体颜色 */
  background: linear-gradient(45deg, #28a745, #11998e, #28a745);    /* 你的成功绿基础色 */
  background-size: 200% auto; /* 放大背景图，让它有移动空间 */
  transition: all 0.4s ease;
  border: none;
  border-radius: 50px;
  overflow: hidden;       /* 必须，为了遮住内部的光影 */
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1); /* 使用贝塞尔曲线让缩放更丝滑 */
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
  z-index: 1;
}

/* 高级感核心：掠过的一道光影 */
.hero-btn::after {
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

/* 悬停时的变化 */
.hero-btn:hover {
  transform: translateY(-5px) scale(1.03); /* 向上漂浮并微扩 */
  box-shadow: 0 12px 25px rgba(40, 167, 69, 0.4);
  background: linear-gradient(45deg, #34ce57, #14b5a9);
  background-position: right center;
}

/* 悬停时触发掠影动画 */
.hero-btn:hover::after {
  left: 100%;
  transition: all 0.7s ease; /* 0.7秒内完成掠影 */
}

/* 激活（点击）瞬间的反馈 */
.hero-btn:active {
  transform: translateY(2px) scale(0.92); /* 点击时轻微下沉收缩，像真实按键 */
  box-shadow: inset 0 2px 5px rgba(40, 167, 69, 0.2);
  transition: transform 0.1s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 鼠标移入时，小图标往右移动 3 像素 */
.hero-btn:hover .icon-move {
  display: inline-block;
  transform: translateX(3px);
  transition: transform 0.3s ease;
}

/* 识别卡片 */
.detection-card {
  border: none;
  border-radius: 12px;
  background: white;
  transition: all 0.3s ease;
}

.detection-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
}

.detection-features h5 {
  font-weight: 600;
  color: #333;
}

.detection-features p {
  margin-bottom: 0;
  font-size: 0.95rem;
}

/* 功能卡片 */
.feature-card {
  border: none;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 2.5rem;
}

/* 分类指南卡片 */
.guide-card {
  border: none;
  border-radius: 16px;
  padding: 0;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.guide-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15) !important;
}

.guide-header {
  /* 使用变量，如果没有定义则默认为蓝色 */
  background: linear-gradient(135deg, var(--theme-color-primary) 0%, var(--theme-color-secondary) 100%);
  box-shadow: 0 4px 15px var(--theme-shadow);
  padding: 25px 20px;
  color: white;
  display: flex;
  align-items: center;
  gap: 10px;
}

.guide-header i {
  display: inline-block; /* 确保滤镜生效 */
  color: white !important;
  -webkit-text-stroke: 1px white;
  /* 给图标加一点微弱的白色光晕，增加精致感 */
  filter: drop-shadow(0 0 3px rgba(255, 255, 255, 0.3));
  /* 增加层级，确保在背景之上 */
  transform: translateZ(0);
  position: relative;
  z-index: 1;
}

.guide-header h5 {
  margin: 0;
  font-weight: 600;
  font-size: 1.5rem;  
  letter-spacing: 2px;
}

/* 动画逻辑 */
.hero-fade-in {
  opacity: 0;
  transform: translateY(30px);
  /* forwards 确保动画结束后停留在最后一帧，不会弹回去 */
  animation: heroTextUp 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}

[class^="animate-"] {
  opacity: 0;
  transform: translateY(30px);
  animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

/* 设置交错延迟，让文字一行行出来 */
.anim-delay-1 { animation-delay: 0.3s; }
.anim-delay-2 { animation-delay: 0.6s; }
.anim-delay-3 { animation-delay: 0.9s; }
/* .anim-delay-4 { animation-delay: 1.2s; } */

.recyclable .guide-header {
  background: linear-gradient(135deg, #0052D4 0%, #4364F7 50%, #6FB1FC 100%);
  box-shadow: 0 4px 15px rgba(0, 82, 212, 0.2);
}

.harmful .guide-header {
  background: linear-gradient(135deg, #e52d27 0%, #b31217 100%);
  box-shadow: 0 4px 15px rgba(179, 18, 23, 0.2);
}

.kitchen .guide-header {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  box-shadow: 0 4px 15px rgba(17, 153, 142, 0.2);
}

.other .guide-header {
  background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%);
  box-shadow: 0 4px 15px rgba(44, 62, 80, 0.2);
}

/* 主描述文字：增加优雅感 */
.main-desc {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #4a5568; /* 柔和的深灰色，比纯黑更有质感 */
  margin-bottom: 20px;
  padding: 0 5px;
}

/* 示例区域整体 */
.example-section {
  background-color: rgba(0, 0, 0, 0.02); /* 极浅的底色，增加层次 */
  border-radius: 12px;
  padding: 15px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

/* “投放示例”标题 */
.example-title {
  font-size: 0.85rem;
  font-weight: bold;
  color: #2d3748;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.example-title i {
  color: #ecc94b; /* 小灯泡用亮金色点缀 */
}

/* 每一行的排版 */
.example-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

/* 左侧类别标签：小徽章风格 */
.category-label {
  background: white;
  color: #4a5568;
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 600;
  min-width: 50px;
  text-align: center;
  margin-right: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  flex-shrink: 0;
}

/* 右侧具体物品 */
.item-tags {
  color: #718096; /* 稍微浅一点的灰色 */
  padding-top: 2px;
}

/* 2. 通用标签样式 */
.category-label {
  background: var(--theme-tag-bg) !important;
  color: var(--theme-tag-text) !important;
  border: 1px solid var(--theme-tag-border) !important;
  /* 其他共有属性保持不变 */
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 600;
  min-width: 50px;
  text-align: center;
  margin-right: 12px;
}

/* 3. 通用小图标颜色 */
.example-title i {
  color: var(--theme-color-primary);
}

/* 可回收物 - 蓝色系 */
.recyclable {
  --theme-color-primary: #3576ca;
  --theme-color-secondary: #6FB1FC;
  --theme-shadow: rgba(0, 82, 212, 0.2);
  --theme-tag-bg: #ebf8ff;
  --theme-tag-text: #2b6cb0;
  --theme-tag-border: #bee3f8;
}

/* 有害垃圾 - 红色系 */
.harmful {
  --theme-color-primary: #e52d27;
  --theme-color-secondary: #b31217;
  --theme-shadow: rgba(179, 18, 23, 0.3);
  --theme-tag-bg: #fff5f5;
  --theme-tag-text: #c53030;
  --theme-tag-border: #feb2b2;
}

/* 厨余垃圾 - 绿色系 */
.kitchen {
  --theme-color-primary: #11998e;
  --theme-color-secondary: #38ef7d;
  --theme-shadow: rgba(17, 153, 142, 0.25);
  --theme-tag-bg: #f0fff4;
  --theme-tag-text: #276749;
  --theme-tag-border: #c6f6d5;
}

/* 其他垃圾 - 灰色系 */
.other {
  --theme-color-primary: #2c3e50;
  --theme-color-secondary: #4ca1af;
  --theme-shadow: rgba(44, 62, 80, 0.25);
  --theme-tag-bg: #d6dee3;
  --theme-tag-text: #4a5568;
  --theme-tag-border: #abb0b6;
}

.guide-content {
  padding: 20px;
}

.guide-content p {
  margin: 0 0 15px 0;
  font-size: 0.95rem;
  line-height: 1.6;
  color: #333;
}

/* 为什么分类 */
.why-important {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 40px;
  border-radius: 12px;
}

.why-important h3 {
  font-weight: 600;
  color: #333;
}

.why-important h6 {
  font-weight: 600;
  margin: 0 0 5px 0;
  color: #333;
}

/* 按钮样式 */
.btn {
  transition: all 0.3s ease;
  border-radius: 8px;
}

.btn:hover {
  transform: translateY(-2px);
}

.btn-lg {
  padding: 15px 40px;
  font-weight: 600;
}

@keyframes heroTextUp {
  0% {
    opacity: 0;
    transform: translateY(40px);
    text-shadow: 0 0 20px rgba(255, 255, 255, 1);
    color: rgba(255, 255, 255, 0); /* 初始文字设为透明，只看阴影 */
  }
  100% {
    opacity: 1;
    transform: translateY(0);
    /* 结束时恢复正常阴影或无阴影 */
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  }
}

/* 定义 Ken Burns 缩放动画 */
@keyframes kenburns {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(1.12);
  }
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .hero-section { height: 100vh; }
  .hero-title { font-size: 2.2rem; }
  .hero-subtitle { font-size: 1.2rem; letter-spacing: 2px; }
  .hero-description { border-left: none; padding-left: 0; text-align: center; }
  .guide-card { margin-bottom: 20px; }
}
</style>