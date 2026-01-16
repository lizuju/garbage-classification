# 垃圾分类检测系统 - 用户端/管理员端部署指南

## 📊 系统架构

本系统实现了用户端和管理员端的完全分离，通过单一 React 应用采用角色路由控制：

- **用户端** (`/user/*`)：普通用户使用垃圾检测功能
- **管理员端** (`/admin/*`)：管理员查看统计数据和系统管理
- **权限守护**：基于 `user.is_admin` 字段自动路由和权限检查

---

## 🚀 快速启动

### 1. 后端启动

```bash
# 进入项目根目录
cd /Users/giovanni/UniversityDocuments/Senior/毕业设计/代码/Garbage_classification_Yolov5

# 激活 conda 环境
conda activate yolov5_env

# 启动 Flask 后端服务
python -m garbage_classification.backend.app
```

**预期输出**：
```
✓ 管理员用户已存在
✓ YOLOv5 路径已验证
* Running on http://127.0.0.1:5001
```

### 2. 前端启动

在新终端中：

```bash
# 进入前端项目目录
cd garbage_classification_frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm start
```

**预期输出**：
```
Compiled successfully!
You can now view the app in browser at http://localhost:3000
```

---

## 🔑 默认凭据

**管理员账号**：
- 用户名: `admin`
- 邮箱: `admin@example.com`
- 密码: `admin123`

**普通用户**：
- 可通过 `/register` 页面自行注册

---

## 📁 前端项目结构

```
garbage_classification_frontend/src/
├── App.js                           # 主应用（路由配置）
├── components/
│   ├── Navbar.js                    # 导航栏（支持角色显示）
│   ├── Footer.js                    # 页脚
│   ├── ProtectedRoute.js            # 权限守护组件
│   ├── User/
│   │   └── UserDashboard.js         # 用户面板（含所有用户路由）
│   └── Admin/
│       └── AdminDashboard.js        # 管理员面板（统计数据）
├── pages/
│   ├── HomePage.js                  # 首页
│   ├── LoginPage.js                 # 登录页
│   ├── RegisterPage.js              # 注册页
│   ├── DetectPage.js                # 垃圾检测页
│   ├── HistoryPage.js               # 识别历史页
│   ├── ProfilePage.js               # 个人资料页
│   └── AboutPage.js                 # 关于页面
└── services/
    └── authService.js               # 认证服务（API 调用）
```

---

## 🌐 路由映射

### 公开路由
| 路由 | 页面 | 说明 |
|------|------|------|
| `/` | 首页 | 项目介绍 |
| `/login` | 登录 | 用户登录 |
| `/register` | 注册 | 用户注册 |
| `/about` | 关于 | 项目信息 |

### 用户路由（需登录，`is_admin=false`）
| 路由 | 页面 | 说明 |
|------|------|------|
| `/user/detect` | 检测页面 | 上传图片进行垃圾分类 |
| `/user/history` | 历史记录 | 查看过去的检测记录 |
| `/user/profile` | 个人资料 | 修改邮箱和密码 |

### 管理员路由（需登录，`is_admin=true`）
| 路由 | 页面 | 说明 |
|------|------|------|
| `/admin` | 仪表板 | 统计数据展示 |
| `/admin/users` | 用户管理 | 用户列表（开发中）|
| `/admin/analytics` | 数据分析 | 分析数据（开发中）|
| `/admin/settings` | 系统设置 | 系统配置（开发中）|

---

## 🔐 权限检查流程

### 1. 初始化
```javascript
// App.js 中
useEffect(() => {
  getCurrentUser();  // 调用 /api/user 检查是否登录
  // 如果返回用户对象，存储到 user state
}, []);
```

### 2. 路由守护
```javascript
// ProtectedRoute.js 中
if (!user) return <Navigate to="/login" />;  // 未登录
if (requiredRole === 'admin' && !user.is_admin)
  return <Navigate to="/" />;  // 权限不足
return children;
```

### 3. 导航栏显示
- **未登录**：显示登录/注册按钮
- **普通用户**：显示 识别检测、识别历史、个人资料
- **管理员**：显示 管理后台、用户名菜单

---

## 📱 后端 API 接口

### 认证接口
| 方法 | 路由 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 用户登录 |
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/logout` | 用户登出 |
| GET | `/api/user` | 获取当前用户 |

### 用户接口
| 方法 | 路由 | 说明 |
|------|------|------|
| GET/PUT | `/api/user/profile` | 获取/更新用户资料 |
| GET | `/api/user/history` | 获取识别历史 |

### 检测接口
| 方法 | 路由 | 说明 |
|------|------|------|
| POST | `/api/detect` | 上传图片检测 |
| GET | `/api/images/<id>/original` | 获取原始图片 |
| GET | `/api/images/<id>/result` | 获取检测结果图片 |

### 管理接口
| 方法 | 路由 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/admin/stats` | 管理员 | 获取统计数据 |
| GET | `/api/admin/users` | 管理员 | 获取用户列表 |
| GET | `/api/admin/logs` | 管理员 | 获取系统日志 |

---

## 🧪 测试场景

### 场景 1：用户注册和登录
1. 访问 `/register`
2. 填写用户名、邮箱、密码（≥8字符）
3. 点击注册，进入登录页
4. 填写用户名和密码登录
5. 自动重定向到 `/user/detect`

### 场景 2：上传图片检测
1. 登录普通用户
2. 进入 `/user/detect`
3. 上传垃圾图片
4. 系统返回检测结果（物品名称、信心度）
5. 结果自动保存到历史记录

### 场景 3：查看识别历史
1. 普通用户登录
2. 点击导航栏 "识别历史"
3. 显示所有过去的检测记录（分页）
4. 每条记录显示检测物品数、平均信心度

### 场景 4：管理员面板
1. 以管理员账号登录（admin/admin123）
2. 导航栏显示 "📊 管理后台"
3. 进入 `/admin`，显示仪表板
4. 展示统计数据：总用户数、总识别数、平均信心度、今日活跃

### 场景 5：权限检查
1. 普通用户直接访问 `/admin`
2. 系统自动重定向到首页 `/`
3. 非登录用户访问任何受保护路由
4. 系统重定向到 `/login`

---

## 🐛 常见问题

### Q1: 登录后仍显示 "请先登录"
**原因**：前端没有在请求中包含 `credentials: 'include'`
**解决**：所有 fetch 调用已默认包含此参数，检查浏览器 Cookie 是否被禁用

### Q2: 管理员账号无法登录
**原因**：数据库中没有管理员用户
**解决**：后端启动时会自动创建，检查后台日志 "✓ 管理员用户已存在"

### Q3: 识别结果返回 "未检测到垃圾物品"
**原因**：上传的图片中没有可识别的物品或图片质量差
**解决**：上传清晰的垃圾物品图片重试

### Q4: 前端样式显示不正确
**原因**：Bootstrap 5 CSS 未加载
**解决**：检查 `public/index.html` 中的 CDN 链接是否正确

---

## 📞 开发提示

### 添加新的用户功能
1. 在 `src/pages/` 创建新页面组件
2. 在 `src/components/User/UserDashboard.js` 中添加路由
3. 在 `Navbar.js` 中添加导航菜单项

### 添加新的管理功能
1. 在 `src/components/Admin/AdminDashboard.js` 中添加新标签页
2. 在后端 `routes/admin.py` 中添加对应 API
3. 在前端调用 `/api/admin/...` 获取数据

### 后端 API 开发
- 所有 API 默认支持会话认证（通过 `@login_required` 装饰器）
- 管理员 API 需要 `@admin_required` 装饰器
- 返回统一的 JSON 格式：`{"status": "success/error", "data": ...}`

---

## 🎯 下一步工作

- [ ] 完善管理员的用户管理页面
- [ ] 添加数据分析和可视化图表
- [ ] 实现系统设置功能
- [ ] 添加邮件通知功能
- [ ] 实现文件导出（CSV/PDF）
- [ ] 性能优化和缓存机制

---

**最后更新**: 2026-01-16
