import os
import sys
import io
import json
import shutil
import time
import secrets
import hashlib
from datetime import datetime
from pathlib import Path
import uuid
import numpy as np
from PIL import ImageDraw, ImageFont
import cv2
import torch
from PIL import Image as PILImage
from flask import Flask, request, jsonify, send_file, render_template, session, redirect, url_for, flash, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

# # 添加YOLOv5路径
# FILE = Path(__file__).resolve()
# ROOT = FILE.parents[2]  # YOLOv5 root directory
# if str(ROOT) not in sys.path:
#     sys.path.append(str(ROOT))

# 文件路径
FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]  # Garbage_classification_Yolov5 根目录
YOLOV5_PATH = ROOT / 'yolov5-6.2'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#  SQLite 数据库路径
db_path = os.path.join(BASE_DIR, 'instance', 'garbage_classification.db')

# 添加 yolov5 路径
if str(YOLOV5_PATH) not in sys.path:
    sys.path.append(str(YOLOV5_PATH))

# sys.path.append('../../yolov5-6.2')
from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, scale_coords
from utils.torch_utils import select_device
from utils.plots import Annotator, colors

# 初始化Flask应用
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)

# 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-should-be-changed'
# 统一使用“绝对路径”的 uploads 目录，避免因启动目录/重载导致相对路径漂移
# ROOT 是项目根目录：Garbage_classification_Yolov5
app.config['UPLOAD_FOLDER'] = str(ROOT / 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///garbage_classification.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'results'), exist_ok=True)

def _resolve_stored_path(stored_path: str):
    """
    兼容历史数据/不同启动目录造成的路径差异：
    - 数据库里可能存了相对路径 uploads/...
    - 或存了 backend/uploads/... 的绝对路径
    - 实际文件可能在 <项目根>/uploads/...
    返回：存在的绝对路径字符串；若找不到返回 None
    """
    if not stored_path:
        return None

    p = Path(stored_path)
    candidates = []

    # 1) 原样（绝对路径或当前可用相对路径）
    candidates.append(p)

    # 2) 若是相对路径：优先按项目根目录拼
    if not p.is_absolute():
        candidates.append(Path(ROOT) / p)
        # 也兼容按 backend 目录拼（少数情况下旧逻辑会这么落盘）
        candidates.append(Path(FILE.parent) / p)

    # 3) 若路径里带 backend/uploads，尝试映射到 <项目根>/uploads
    try:
        backend_uploads = (Path(FILE.parent) / 'uploads').resolve()
        root_uploads = (Path(ROOT) / 'uploads').resolve()
        if str(backend_uploads) in str(p):
            candidates.append(Path(str(p).replace(str(backend_uploads), str(root_uploads))))
    except Exception:
        pass

    for c in candidates:
        try:
            cp = c.resolve() if not c.is_absolute() else c
            if cp.exists():
                return str(cp)
        except Exception:
            continue
    return None

# 初始化数据库
db = SQLAlchemy(app)

# 定义数据模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_path = db.Column(db.String(255), nullable=False)
    result_path = db.Column(db.String(255), nullable=True)
    result_data = db.Column(db.Text, nullable=True)  # JSON格式的检测结果
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('images', lazy=True))

class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_type = db.Column(db.String(20), nullable=False)  # 'info', 'error', 'user_action'
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('logs', lazy=True))

class DetectionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    image_path = db.Column(db.String(255), nullable=False)
    result = db.Column(db.Text, nullable=False)  # JSON结果
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_path': self.image_path,
            'result': json.loads(self.result),
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat()
        }

# 创建数据库表
with app.app_context():
    db.create_all()
    
    # 添加默认管理员账号（如果不存在）
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# 加载YOLOv5模型
def load_model():
    try:
        # 1. 优先级路径列表
        search_paths = [
            ROOT / 'best.pt',
            YOLOV5_PATH / 'runs/train/garbage_model/weights/best.pt',
            YOLOV5_PATH / 'best.pt',
            YOLOV5_PATH / 'yolov5m.pt',
            YOLOV5_PATH / 'yolov5s.pt'
        ]

        weights = None
        for path in search_paths:
            if path.exists():
                weights = path
                print(f"成功定位模型文件: {weights}")
                break
        
        if weights is None:
            raise FileNotFoundError("❌ 未能找到任何权重文件 (.pt)")

        # 2. 设备选择逻辑 (增加 MPS 支持)
        # 自动尝试顺序：CUDA (NVIDIA) -> MPS (Apple Silicon) -> CPU
        device = torch.device('cpu')
        if torch.cuda.is_available():
            device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            device = torch.device('mps')
            print("正在使用 Apple Silicon MPS 加速...")
        else:
            print("未检测到 GPU 加速，使用 CPU 推理...")

        # 3. 加载模型
        model = attempt_load(weights, device=device)
        
        # 4. 获取模型属性与图像尺寸检查
        stride = int(model.stride.max())
        imgsz = check_img_size(640, s=stride)

        # 5. 半精度处理 (FP16)
        # 注意：MPS 完美支持 half()，能极大提升 Mac 上的速度
        # 但在某些旧版 PyTorch 中，MPS 的 half 可能不稳定，若报错请改用 model.float()
        is_gpu = device.type in ['cuda', 'mps']
        if is_gpu:
            model.half()
        else:
            model.float()

        # 6. 模型预热 (Warmup)
        print(f"正在预热模型 ({device.type})...")
        warmup_img = torch.zeros(1, 3, imgsz, imgsz).to(device)
        if is_gpu:
            warmup_img = warmup_img.half()
        else:
            warmup_img = warmup_img.float()
            
        model(warmup_img)
        
        print(f"✅ 模型初始化完成，使用设备: {device}")
        return model, device, imgsz, stride

    except Exception as e:
        print(f"🚨 加载模型出错: {e}")
        return None, None, None, None

model, device, imgsz, stride = load_model()
# 根据训练数据更新模型类别名称
class_names = ['可回收', '有害', '厨余', '其他']  # 模型类别名称，这里使用原有的四分类

# 判断文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# 认证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'status': 'error', 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'status': 'error', 'message': '请先登录'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'status': 'error', 'message': '需要管理员权限'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

# 记录日志的工具函数
def log_action(log_type, message, user_id=None):
    log = SystemLog(log_type=log_type, message=message, user_id=user_id)
    db.session.add(log)
    db.session.commit()

# 图像检测函数
def detect_garbage_image(img_bytes):
    if model is None or device is None:
        return [], None
        
    img = PILImage.open(io.BytesIO(img_bytes)).convert('RGB')
    
    # 调整图像大小为模型需要的尺寸
    img_size = imgsz  # 使用模型加载时确定的尺寸
    img = img.resize((img_size, img_size), PILImage.LANCZOS)
    img_array = np.array(img)
    
    # 预处理图像
    img_tensor = torch.from_numpy(img_array.transpose(2, 0, 1)).to(device)
    img_tensor = img_tensor / 255.0
    # 仅在 GPU 上转为 half，CPU 保持 float32
    if device.type != 'cpu':
        img_tensor = img_tensor.half()
    else:
        img_tensor = img_tensor.float()
    if img_tensor.ndimension() == 3:
        img_tensor = img_tensor.unsqueeze(0)
    
    # 推理
    with torch.no_grad():
        pred = model(img_tensor, augment=False)[0]
    
    print(f"模型输出尺寸: {pred.shape}")
    print(f"预测结果: 最大值={torch.max(pred).item()}, 最小值={torch.min(pred).item()}")
    
    # 应用NMS - 使用置信度阈值0.1
    pred = non_max_suppression(pred, 0.1, 0.45, None, False, max_det=1000)
    
    print(f"NMS后检测到的物体数量: {len(pred[0])}")
    
    # 保存原始尺寸用于显示
    display_img = PILImage.open(io.BytesIO(img_bytes)).convert('RGB')
    
    # 创建PIL图像用于绘制(而不是numpy数组)
    result_img_pil = display_img.copy()
    draw = ImageDraw.Draw(result_img_pil)
    
    # 尝试加载中文字体，如果失败则使用默认字体
    # 加载中文字体（跨平台）
    def load_chinese_font(size=16):
        font_paths = [
            # macOS
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/Library/Fonts/Arial Unicode.ttf",

            # Windows
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/simkai.ttf",

            # Linux（以防万一）
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
        ]

        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    pass

        # 兜底（不推荐，但保证不崩）
        return ImageFont.load_default()

    # 使用字体
    font = load_chinese_font(16)

    # 处理结果
    results = []
    display_array = np.array(display_img)
    
    for i, det in enumerate(pred):
        if len(det):
            # 将坐标从调整尺寸的图像缩放回原始图像尺寸
            det_scaled = det.clone()
            scale_factor = [display_array.shape[1]/img_size, display_array.shape[0]/img_size, 
                          display_array.shape[1]/img_size, display_array.shape[0]/img_size, 1, 1]
            det_scaled[:, :4] = det_scaled[:, :4] * torch.tensor(scale_factor[:4], device=det.device)
            
            # 处理每个检测框
            for *xyxy, conf, cls in reversed(det_scaled):
                c = int(cls)
                # 获取边界框坐标
                x1, y1, x2, y2 = [int(x) for x in xyxy]
                
                # 设置颜色 (RGB格式)
                if c == 0:  # 可回收
                    color = (0, 200, 0)  # 绿色
                elif c == 1:  # 有害垃圾
                    color = (255, 0, 0)  # 红色
                elif c == 2:  # 厨余垃圾
                    color = (255, 165, 0)  # 橙色
                else:  # 其他垃圾
                    color = (128, 128, 128)  # 灰色
                
                # 绘制矩形
                draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=2)
                
                # 绘制标签背景
                label = f"{class_names[c]} {conf:.2f}"
                label_size = draw.textbbox((0, 0), label, font=font)[2:]
                
                if y1 - label_size[1] - 5 > 0:
                    text_origin = (x1, y1 - label_size[1] - 5)
                else:
                    text_origin = (x1, y1 + 5)
                
                # 绘制标签背景
                draw.rectangle(
                    [text_origin[0], text_origin[1], 
                     text_origin[0] + label_size[0], text_origin[1] + label_size[1]],
                    fill=color
                )
                
                # 绘制标签文本(白色)
                draw.text(text_origin, label, fill=(255, 255, 255), font=font)
                
                results.append({
                    'class': c,
                    'class_name': class_names[c],
                    'confidence': float(conf),
                    'bbox': [float(x) for x in xyxy]
                })
    
    return results, result_img_pil

# 路由：主页
@app.route('/')
def index():
    return render_template('index.html')

# 路由：登录页面
@app.route('/login')
def login_page():
    return render_template('login.html')

# 路由：注册页面
@app.route('/register')
def register_page():
    return render_template('register.html')

# 路由：检测页面
@app.route('/detect')
def detect_page():
    return render_template('detect.html')

# 路由：历史记录页面
@app.route('/history')
def history_page():
    return render_template('history.html')

# 路由：关于页面
@app.route('/about')
def about_page():
    return render_template('about.html')

# 路由：个人信息页面
@app.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html')

# 路由：管理员页面
@app.route('/admin')
@admin_required
def admin_page():
    return render_template('admin.html')

# API：注册
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 检查必填字段
    if not all(field in data for field in ['username', 'email', 'password']):
        return jsonify({'status': 'error', 'message': '缺少必要字段'}), 400
    
    # 检查用户名或邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'status': 'error', 'message': '用户名已存在'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'status': 'error', 'message': '邮箱已被注册'}), 400
    
    # 创建新用户
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    
    # 如果是第一个用户，设置为管理员
    if User.query.count() == 0:
        user.is_admin = True
    
    db.session.add(user)
    
    try:
        db.session.commit()
        log_action('user_action', f'用户注册: {data["username"]}')
        return jsonify({'status': 'success', 'message': '注册成功', 'user': user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'注册失败: {str(e)}'}), 500

# API：登录
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # 检查必填字段
    if not all(field in data for field in ['username', 'password']):
        return jsonify({'status': 'error', 'message': '缺少必要字段'}), 400
    
    # 查找用户
    user = User.query.filter_by(username=data['username']).first()
    
    # 验证密码
    if user and user.check_password(data['password']):
        session['user_id'] = user.id
        log_action('user_action', f'用户登录: {user.username}', user.id)
        return jsonify({'status': 'success', 'message': '登录成功', 'user': user.to_dict()}), 200
    
    return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401

# API：注销
@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if user:
        log_action('user_action', f'用户登出: {user.username}', user_id)
    
    session.pop('user_id', None)
    return jsonify({'status': 'success', 'message': '注销成功'}), 200

# API：检测垃圾分类
@app.route('/api/detect', methods=['POST'])
@login_required
def detect():
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': '没有文件'}), 400
        
    file = request.files['file']
    
    # 检查文件名
    if file.filename == '':
        return jsonify({'status': 'error', 'message': '没有选择文件'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': f'只支持 {", ".join(app.config["ALLOWED_EXTENSIONS"])} 格式图像'}), 400
    
    try:
        # 读取文件内容
        file_bytes = file.read()
        
        # 保存原始图像
        filename = secure_filename(file.filename)
        unique_id = uuid.uuid4().hex
        unique_filename = f"{unique_id}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_bytes)
        
        # 执行检测
        results, result_img = detect_garbage_image(file_bytes)
        
        # 即使未检测到物体也继续处理，不返回404
        # 保存结果图像
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], 'results', f"{unique_id}_result.jpg")
        result_img.save(result_path)
        
        # 保存到数据库
        result_json = json.dumps(results, ensure_ascii=False) if results else "[]"
        image = Image(
            filename=unique_filename,
            original_path=file_path,
            result_path=result_path,
            result_data=result_json,
            user_id=session['user_id']
        )
        db.session.add(image)
        
        # 记录到检测历史
        confidence = max([item.get('confidence', 0) for item in results]) if results else 0
        history = DetectionHistory(
            user_id=session['user_id'],
            image_path=file_path,
            result=result_json,
            confidence=confidence
        )
        db.session.add(history)
        db.session.commit()
        
        log_action('user_action', f'Detection finished: {len(results)} objects', session['user_id'])
        
        # 返回结果 (即使未检测到物体也返回200状态码)
        return jsonify({
            'status': 'success',
            'image_id': image.id,
            'results': results,
            'original_url': f"/api/images/{image.id}/original",
            'result_url': f"/api/images/{image.id}/result",
            'history_id': history.id,
            'message': '识别完成' if results else '未检测到垃圾物品'
        }), 200
        
    except Exception as e:
        # 回滚本次事务，避免会话处于错误状态
        db.session.rollback()
        log_action('error', f'识别错误: {str(e)}', session.get('user_id'))
        return jsonify({'status': 'error', 'message': f'处理图像时出错: {str(e)}'}), 500

# API：获取原始图像
@app.route('/api/images/<int:image_id>/original')
@login_required
def get_original_image(image_id):
    image = Image.query.get_or_404(image_id)
    
    # 检查权限
    if image.user_id != session['user_id'] and not User.query.get(session['user_id']).is_admin:
        return jsonify({'status': 'error', 'message': '无权访问此图像'}), 403

    resolved = _resolve_stored_path(image.original_path)
    if not resolved:
        return jsonify({'status': 'error', 'message': '原始图片文件不存在或路径无效'}), 404
    return send_file(resolved)

# API：获取结果图像
@app.route('/api/images/<int:image_id>/result')
@login_required
def get_result_image(image_id):
    image = Image.query.get_or_404(image_id)
    
    # 检查权限
    if image.user_id != session['user_id'] and not User.query.get(session['user_id']).is_admin:
        return jsonify({'status': 'error', 'message': '无权访问此图像'}), 403

    resolved = _resolve_stored_path(image.result_path)
    if not resolved:
        return jsonify({'status': 'error', 'message': '结果图片文件不存在或尚未生成'}), 404
    return send_file(resolved)

# API：获取所有用户（管理员）
@app.route('/api/admin/users')
@admin_required
def list_users():
    users = User.query.all()
    user_list = [user.to_dict() for user in users]
    return jsonify({'status': 'success', 'users': user_list}), 200

# API：获取系统日志（管理员）
@app.route('/api/admin/logs')
@admin_required
def list_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    logs_query = SystemLog.query.order_by(SystemLog.created_at.desc())
    pagination = logs_query.paginate(page=page, per_page=per_page, error_out=False)
    
    logs = []
    for log in pagination.items:
        log_dict = {
            'id': log.id,
            'log_type': log.log_type,
            'message': log.message,
            'user_id': log.user_id,
            'created_at': log.created_at.isoformat()
        }
        
        if log.user_id:
            user = User.query.get(log.user_id)
            if user:
                log_dict['username'] = user.username
        
        logs.append(log_dict)
    
    return jsonify({
        'status': 'success',
        'logs': logs,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

# API：获取系统统计数据（管理员）
@app.route('/api/admin/stats')
@admin_required
def get_stats():
    # 用户统计
    total_users = User.query.count()
    new_users_today = User.query.filter(
        User.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    
    # 图像统计
    total_images = Image.query.count()
    images_today = Image.query.filter(
        Image.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    
    # 分类统计
    class_counts = {}
    for class_name in class_names:
        class_counts[class_name] = 0
    
    for image in Image.query.all():
        if image.result_data:
            try:
                results = json.loads(image.result_data)
                for result in results:
                    class_name = result.get('class_name')
                    if class_name in class_counts:
                        class_counts[class_name] += 1
            except:
                pass
    
    return jsonify({
        'status': 'success',
        'users': {
            'total': total_users,
            'new_today': new_users_today
        },
        'images': {
            'total': total_images,
            'new_today': images_today
        },
        'classes': class_counts
    })

# API：获取用户个人资料
@app.route('/api/user/profile')
@login_required
def get_user_profile():
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
        
    return jsonify({
        'status': 'success',
        'user': user.to_dict()
    }), 200

# API：修改密码
@app.route('/api/user/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    
    # 检查必填字段
    if not all(field in data for field in ['old_password', 'new_password']):
        return jsonify({'status': 'error', 'message': '缺少必要字段'}), 400
        
    user = User.query.get(session['user_id'])
    
    # 验证旧密码
    if not user.check_password(data['old_password']):
        return jsonify({'status': 'error', 'message': '旧密码不正确'}), 401
        
    # 更新密码
    user.set_password(data['new_password'])
    db.session.commit()
    
    log_action('user_action', '用户修改密码', user.id)
    
    return jsonify({
        'status': 'success',
        'message': '密码已更新'
    }), 200

# API：获取用户历史检测记录
@app.route('/api/user/history')
@login_required
def get_user_history():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    history_query = Image.query.filter_by(user_id=session['user_id']).order_by(Image.created_at.desc())
    pagination = history_query.paginate(page=page, per_page=per_page, error_out=False)
    
    history_list = []
    for image in pagination.items:
        try:
            results = json.loads(image.result_data) if image.result_data else []
            
            history_list.append({
                'id': image.id,
                'filename': image.filename,
                'results': results,
                'created_at': image.created_at.isoformat(),
                'original_url': f"/api/images/{image.id}/original",
                'result_url': f"/api/images/{image.id}/result"
            })
        except:
            pass
            
    return jsonify({
        'status': 'success',
        'history': history_list,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

# API：获取当前用户信息
@app.route('/api/user', methods=['GET'])
def get_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    user = db.session.get(User, user_id)
    if not user:
        session.pop('user_id', None)
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    return jsonify({'status': 'success', 'user': user.to_dict()}), 200

# 路由：获取上传的图片
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 初始化数据库
@app.before_first_request
def initialize_database():
    db.create_all()

# 启动应用
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)