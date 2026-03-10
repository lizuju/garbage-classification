# 🗑️ YOLOv5 垃圾分类识别系统

本项目是一个**前后端分离的垃圾分类识别平台**，基于 YOLOv5 分类模型，提供完整的用户体系、管理员后台、日志与统计、历史记录管理以及模型训练与迭代流程。适用于毕业设计、科研验证与工程化落地。

---

## 🧭 系统介绍

该系统围绕"**垃圾图像上传 → YOLOv5 识别 → 分类结果展示 → 记录与管理**"的完整链路构建，覆盖了从模型训练到业务落地的主要环节：

- **模型层**：基于 YOLOv5x-cls 图像分类架构，支持 **265 个细分类别**（映射到可回收、有害、厨余、其他四大类）。模型采用 448×448 输入、ImageNet 归一化预处理、Softmax 概率输出，推理时支持自动选择 CUDA / MPS / CPU 设备，GPU 模式下启用 FP16 半精度加速。实时检测模式还引入滑动窗口帧平均策略，抑制单帧抖动，提升稳定性。权重文件位于 `garbage265_hierarchical/weights/best.pt`。
- **服务层**：Flask 后端提供 REST API，承担身份认证、检测调用、记录管理、日志审计等核心逻辑。
- **交互层**：Vue 3 前端提供用户端与管理员端界面，包含识别、历史、资料修改、管理后台等功能。

系统既适合作为"AI+业务"的工程实践，也可作为课程设计/毕业设计的完整方案。

---

## ✨ 项目亮点

- **双头层级 YOLOv5 模型**：基于 YOLOv5x-cls 训练的双头分类模型，支持 265 类细粒度识别与 4 大类联合优化，具备帧平均实时推理、FP16 加速与多设备自适应等能力（详见「模型核心技术」章节）。
- **前后端分离架构**：前端 Vue 3 + Vite，后端 Flask，部署与扩展更灵活。
- **前端 UI 设计突出**：界面风格统一、玻璃拟态卡片、动效与过渡自然，整体体验更接近工业级产品。
- **多角色权限体系**：管理员/普通用户分级管理，权限边界清晰。
- **完整后台管理闭环**：用户管理、操作日志、统计面板、数据导出齐全。
- **回收地图智能导航**：集成高德地图，支持附近回收点检索、筛选、详情展示与导航跳转。
- **工程化可维护**：结构清晰，模块划分明确，适合二次开发与功能扩展。

---

## 🎨 前端 UI 风格与交互设计

- **整体视觉统一**：组件风格一致，配色克制且清晰，信息层级明确  
- **卡片玻璃拟态**：重点内容采用玻璃拟态卡片，提升质感  
- **动效过渡自然**：页面切换、弹窗进入、列表交互具有柔和过渡  
- **可读性优先**：字体与间距经过统一设计，减少视觉噪声  
- **移动端适配**：关键模块支持响应式布局，保证移动端体验  

---

## 🤖 模型核心技术

- **YOLOv5x-cls 高精度分类**：使用 YOLOv5x 最大档分类模型在 265 类细粒度垃圾数据集上训练，识别精度显著优于通用检测模型。  
- **双头层级训练（`major_weight=0.5`）**：同时优化 265 个细分类别与 4 大类主类，主副类损失等权联合回传，单次推理直接获得精细结果与大类归属，防止模型偏向细粒度而忽视大类语义。  
- **标签平滑抑制过拟合**：`label_smoothing=0.1` 使概率输出更平滑，减少对噪声标注的记忆，泛化能力更强。  
- **高分辨率输入（448×448）**：优于标准 224，更完整保留外观细节，对外形相似垃圾（如不同类型塑料瓶）区分效果更佳。  
- **ImageNet 迁移 + Adam 微调**：基于预训练权重，`lr0=0.001` + Adam 精细微调，收敛更快且精度更高。  
- **多设备自适应 + FP16 加速**：自动选择 CUDA / Apple MPS / CPU，GPU 模式启用 FP16 半精度，推理速度提升约 1.5~2×，显存占用减半。  
- **帧平均稳定实时识别**：摄像头模式下对连续 3 帧概率取均值，彻底消除单帧抖动，识别结果更稳定。  
- **类别名称智能映射**：通过 `classname.txt` + ImageNet 字典序双重映射，将数字索引准确还原为中文垃圾细分名称。  
- **权重热替换持续迭代**：新权重放置指定路径后重启即生效，无需修改任何配置，支持模型快速上线与持续优化。  

---

## 🗺️ 回收地图功能

- **登录后可用**：与识别检测一致，未登录用户触发登录引导，保证功能权限一致性。  
- **地图能力**：接入高德地图，支持定位、地图展示与"重新定位并搜索"。  
- **检索范围可调**：支持 `1km / 3km / 5km / 10km / 15km` 半径搜索。  
- **分类筛选**：支持"全部回收点、可回收物、厨余垃圾、有害垃圾、其他垃圾"筛选。  
- **交互联动**：点击列表项可联动地图 Marker 高亮，点击 Marker 也会同步选中列表项。  
- **详情增强**：选中回收点展示地址、电话、营业时间、评分、区域、距离等信息。  
- **导航能力**：支持一键"进入导航"，跳转高德导航链接。  
- **体验优化**：地图加载遮罩、选中态动画、卡片化信息布局与移动端适配。  

---

## ✅ 环境要求

**后端（Flask）**
- Python 3.8+
- pip / virtualenv
- 常用依赖：Flask、SQLAlchemy、PyJWT、PyTorch、torchvision、Pillow 等

**前端（Vue 3）**
- Node.js 16+（建议 18+）
- npm 8+
- Vite 构建工具
- 高德地图 Web API Key（用于回收地图能力）

**模型训练（YOLOv5 classify）**
- PyTorch 1.8+
- CUDA（推荐，GPU 加速训练）
- 数据集需满足 ImageFolder 格式（每类一个子文件夹）

---

## 📁 完整项目结构

```
Garbage_classification_Yolov5/
│
├── README.md
├── garbage.yaml                  # 数据集配置（4大类，用于检测模式参考）
├── classname.txt                 # 265个细分类别名称（中文）
├── LICENSE
├── run_detect.sh
│
├── garbage265_hierarchical/      # 🧠 训练产出目录
│   ├── opt.yaml                  # 训练配置快照（epochs/batch/imgsz等）
│   ├── results.csv               # 各 epoch 训练指标记录
│   ├── results.png               # 训练曲线可视化
│   ├── train_images.jpg          # 训练样本预览
│   ├── test_images.jpg           # 测试样本预览
│   └── weights/
│       ├── best.pt               # ✅ 最优权重（系统加载此文件）
│       ├── last.pt               # 最后一轮权重
│       └── best.mlpackage/       # CoreML 导出包（Apple 设备推理）
│
├── uploads/
│   └── results/
│
├── datasets/
│   ├── coco128/
│   └── wangy/                    # 训练数据集（ImageFolder 格式）
│
├── garbage_classification/       # 🔧 Flask 后端
│   ├── __init__.py
│   └── backend/
│       ├── app.py                # 应用入口
│       ├── config.py             # 配置管理
│       ├── extensions.py         # Flask 扩展初始化
│       ├── models/               # 数据库模型（ORM）
│       ├── routes/               # API 路由层
│       ├── services/
│       │   ├── yolo_service.py   # YOLOv5 推理核心服务
│       │   ├── auth_service.py   # 身份认证
│       │   ├── jwt_service.py    # JWT 管理
│       │   ├── log_service.py    # 日志服务
│       │   └── admin_service.py  # 管理员服务
│       ├── managers/             # 业务管理层
│       ├── utils/                # 工具函数
│       ├── templates/            # Jinja2 模板（备用）
│       ├── static/               # 静态资源
│       ├── uploads/              # 用户上传图片存储
│       └── instance/             # SQLite 数据库实例
│
├── garbage_classification_frontend/   # 🖥️ Vue 3 前端
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── public/
│   └── src/
│       ├── App.vue
│       ├── main.js
│       ├── assets/
│       ├── components/           # 可复用组件
│       │   ├── CameraDetect.vue  # 实时摄像头识别
│       │   ├── AuthModal.vue     # 登录/注册弹窗
│       │   ├── Navbar.vue        # 导航栏
│       │   └── ...
│       ├── composables/
│       │   └── useRecycleMap.js  # 地图逻辑 Composable
│       ├── config/
│       │   └── recycleMapConfig.js
│       ├── pages/                # 页面组件
│       │   ├── RecycleMapPage.vue
│       │   ├── AdminPage.vue
│       │   └── ...
│       ├── router/               # Vue Router 路由配置
│       ├── services/
│       │   └── amapService.js    # 高德地图服务封装
│       ├── styles/               # CSS 样式（分页面/全局）
│       └── directives/           # 自定义指令
│
└── yolov5/                       # 📦 YOLOv5 源码
    ├── classify/                 # 🏷️ 分类模式（本项目主要使用）
    │   ├── train.py              # ✅ 分类训练入口
    │   ├── val.py                # 分类验证脚本
    │   └── predict.py            # 单图快速预测
    ├── detect.py                 # 目标检测推理
    ├── train.py                  # 目标检测训练
    ├── val.py                    # 目标检测验证
    ├── export.py                 # 模型导出（ONNX/CoreML/TFLite等）
    ├── requirements.txt
    ├── best.pt                   # 训练产出权重备份
    ├── yolov5m.pt                # yolov5m 预训练权重
    ├── models/                   # 模型结构定义
    ├── utils/                    # YOLOv5 工具库
    ├── data/                     # 数据集配置文件
    └── runs/
        └── train/                # 历次训练产出（exp ~ exp8）
```

---

## 🚀 部署流程

### 1) 启动后端
```bash
python -m garbage_classification.backend.app
```

### 2) 启动前端
```bash
cd garbage_classification_frontend
npm run dev
```

---

## 🧠 训练模型流程

本项目模型基于 **YOLOv5x-cls**（YOLOv5 最大档分类网络）进行迁移学习，在自建的 **garbage265** 数据集上训练，支持 265 个细分类别与 4 个主类的联合优化。

### 第一步：准备数据集

数据集需采用 **ImageFolder 格式**，每个类别一个子文件夹：

```
garbage265/
├── train/
│   ├── 其他垃圾-一次性快餐盒/
│   │   ├── img_001.jpg
│   │   └── ...
│   ├── 厨余垃圾-剩饭剩菜/
│   └── ...  (共 265 个类别文件夹)
└── val/
    ├── 其他垃圾-一次性快餐盒/
    └── ...
```

> 类别与 ID 的对应关系见 `classname.txt`（按字典序排列）。

### 第二步：配置训练参数

进入 `yolov5/` 目录，根据需要调整以下关键参数：

| 参数 | 本项目使用值 | 说明 |
|---|---|---|
| `--model` | `yolov5x-cls.pt` | 预训练基础模型（最大档，精度最高） |
| `--data` | `/path/to/garbage265` | 数据集根目录（ImageFolder 格式） |
| `--epochs` | `80` | 训练轮数 |
| `--batch-size` | `128` | 批次大小（32GB 显存可支持） |
| `--imgsz` | `448` | 训练输入分辨率（448 优于 224） |
| `--device` | `0` | GPU 设备编号（RTX 5090 单卡） |
| `--optimizer` | `Adam` | 优化器 |
| `--lr0` | `0.001` | 初始学习率 |
| `--label-smoothing` | `0.1` | 标签平滑，防止过拟合 |
| `--workers` | `8` | 数据加载线程数 |
| `--pretrained` | 启用 | 使用 ImageNet 预训练权重迁移学习 |

### 第三步：启动训练

```bash
cd yolov5

python classify/train.py \
  --model yolov5x-cls.pt \
  --data /path/to/garbage265 \
  --epochs 80 \
  --batch-size 128 \
  --imgsz 448 \
  --device 0 \
  --optimizer Adam \
  --lr0 0.001 \
  --label-smoothing 0.1 \
  --workers 8 \
  --pretrained \
  --project runs/train-cls \
  --name garbage265_hierarchical
```

训练产出保存在 `runs/train-cls/garbage265_hierarchical/`，包含：
- `weights/best.pt` — 验证集最优权重
- `weights/last.pt` — 最后一轮权重
- `results.csv` — 每轮训练指标（Top1/Top5 Acc、Loss）
- `results.png` — 训练曲线图

### 第四步：部署权重

将训练好的 `best.pt` 复制到系统指定路径，后端将自动加载：

```bash
cp runs/train-cls/garbage265_hierarchical/weights/best.pt \
   ../garbage265_hierarchical/weights/best.pt
```

系统启动时，`YoloService` 会自动从 `garbage265_hierarchical/weights/best.pt` 加载模型，无需修改任何配置文件。

### 第五步：验证模型效果

```bash
# 在验证集上评估 Top1/Top5 准确率
python classify/val.py \
  --weights ../garbage265_hierarchical/weights/best.pt \
  --data /path/to/garbage265 \
  --imgsz 448 \
  --device 0

# 单图快速预测
python classify/predict.py \
  --weights ../garbage265_hierarchical/weights/best.pt \
  --source /path/to/test_image.jpg \
  --imgsz 448
```

> 训练过程经过 **8 次实验迭代**（exp ~ exp8），最终产出的 `best.pt`（~90MB）为系统当前使用的生产权重。

---

## 🔐 权限与安全策略

- JWT 认证保护关键接口
- 管理员与用户权限隔离
- 管理员不可禁用（后端校验）
- 最后一个管理员不可降级
- 登录状态与接口权限严格区分，避免越权访问
- 关键行为写入日志，便于审计与追踪

---

## 📊 统计与监控

- 统计面板包含检测量、用户数、活跃度、平均置信度
- 支持操作日志审计，管理员可追踪关键行为
- 数据导出支持运营与模型分析
- 管理后台支持多维度系统状态查看

---

## 🧪 测试建议

**核心流程测试**
- 注册 / 登录 / 记住我 / 注销
- 图片上传与识别
- 历史记录生成与查询
- 个人资料修改与密码变更

**管理后台测试**
- 用户编辑 / 禁用 / 恢复
- 权限限制（普通用户访问后台）
- 数据统计与导出
- 日志列表分页

---

## 📄 许可证

本项目遵循仓库内 `LICENSE` 约束。
