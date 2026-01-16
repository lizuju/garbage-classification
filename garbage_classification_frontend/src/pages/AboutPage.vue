<template>
  <div class="container mt-5">
    <div class="row">
      <div class="col-md-8 offset-md-2">
        <div class="card">
          <div class="card-body">
            <h2 class="card-title">关于项目</h2>
            <p class="lead">垃圾分类智能识别系统</p>

            <h4 class="mt-4">项目概述</h4>
            <p>
              本系统是一个基于深度学习（YOLOv5）的垃圾自动分类识别系统。用户上传垃圾图片后，系统能快速准确地识别垃圾类别，帮助用户进行正确的垃圾分类。
            </p>

            <h4 class="mt-4">主要功能</h4>
            <ul>
              <li>图片上传与实时预览</li>
              <li>AI 智能垃圾检测与分类</li>
              <li>识别历史记录保存</li>
              <li>用户管理与权限控制</li>
              <li>管理后台统计与分析</li>
            </ul>

            <h4 class="mt-4">技术栈</h4>
            <ul>
              <li><strong>后端：</strong>Flask + SQLAlchemy + YOLOv5</li>
              <li><strong>前端：</strong>Vue 3 + Vite + Bootstrap 5</li>
              <li><strong>数据库：</strong>SQLite</li>
              <li><strong>部署：</strong>本地或云端服务器</li>
            </ul>

            <h4 class="mt-4">垃圾分类标准</h4>
            <div class="row mt-3">
              <div class="col-md-3">
                <div class="card text-center">
                  <div class="card-body">
                    <span class="category-label recyclable">可回收</span>
                    <p class="mt-2 small">纸张、塑料、金属、玻璃等</p>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card text-center">
                  <div class="card-body">
                    <span class="category-label harmful">有害</span>
                    <p class="mt-2 small">电池、灯泡、化学品等</p>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card text-center">
                  <div class="card-body">
                    <span class="category-label kitchen">厨余</span>
                    <p class="mt-2 small">食物、果皮、餐厨垃圾</p>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card text-center">
                  <div class="card-body">
                    <span class="category-label other">其他</span>
                    <p class="mt-2 small">其他无法分类的垃圾</p>
                  </div>
                </div>
              </div>
            </div>

            <h4 class="mt-4">联系我们</h4>
            <p>
              如有问题或建议，欢迎通过以下方式联系我们：
              <br />
              <i class="bi bi-envelope me-2"></i>Email: contact@example.com
              <br />
              <i class="bi bi-telephone me-2"></i>Phone: (123) 456-7890
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
//
</script>

<style scoped>
.card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.category-label {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 0.875rem;
}

.category-label.recyclable {
  background-color: #28a745;
}

.category-label.harmful {
  background-color: #dc3545;
}

.category-label.kitchen {
  background-color: #fd7e14;
}

.category-label.other {
  background-color: #6c757d;
}

h4 {
  color: #2c3e50;
  font-weight: 600;
  margin-top: 20px;
  border-bottom: 2px solid #28a745;
  padding-bottom: 10px;
}
</style>
