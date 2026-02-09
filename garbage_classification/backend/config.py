import os
from pathlib import Path


class Config:
    """
    统一管理配置（论文里也好写）：
    - 路径(项目根、YOLOv5 目录、uploads、db)
    - Flask/SQLAlchemy 配置
    """

    FILE = Path(__file__).resolve()

    # 从 backend/config.py 开始，逐层向上找 yolov5-6.2
    YOLOV5_PATH = None
    for parent in FILE.parents:
        candidate = parent / 'yolov5-6.2'
        if candidate.exists():
            YOLOV5_PATH = candidate
            break
    if YOLOV5_PATH is None:
        raise RuntimeError("❌ 未找到 yolov5-6.2 目录，请检查项目结构")

    ROOT = YOLOV5_PATH.parent  # 项目根目录（Garbage_classification_Yolov5）
    BASE_DIR = FILE.parent  # backend/

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-should-be-changed')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    # JWT 配置
    JWT_SECRET = os.environ.get('JWT_SECRET', 'jwt-dev-key-should-be-changed')
    JWT_EXPIRATION = 24 * 60 * 60  # 24小时
    JWT_EXPIRATION_REMEMBER = 7 * 24 * 60 * 60  # 7天（记住我）

    # 上传目录：统一走项目根 uploads
    UPLOAD_FOLDER = str(ROOT / 'uploads')

    # SQLite（固定到 backend/instance 下）
    DB_PATH = str(BASE_DIR / 'instance' / 'garbage_classification.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session 配置
    PERMANENT_SESSION_LIFETIME = 24 * 60 * 60  # 24小时
    SESSION_COOKIE_SECURE = False  # 开发环境设为False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # 防止CSRF，允许same-site请求
    SESSION_COOKIE_NAME = 'gc_session'
