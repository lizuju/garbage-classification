import os
from pathlib import Path

from flask import Flask, send_from_directory, session

from .config import Config
from .extensions import db, cors
from .models import User  # noqa: F401  # ensure models are registered
from .routes import pages_bp, auth_bp, detect_bp, admin_bp, user_bp
from .services.yolo_service import YoloService


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    # 额外放两个路径给工具函数用
    app.config['PROJECT_ROOT'] = Path(Config.ROOT)
    app.config['BACKEND_DIR'] = Path(Config.BASE_DIR)

    # init extensions
    db.init_app(app)
    cors.init_app(app, supports_credentials=True, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5001", "http://127.0.0.1:5001", "http://192.168.31.190:5001"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })

    # 为所有请求启用永久会话
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    # uploads dir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'results'), exist_ok=True)
    os.makedirs(os.path.join(app.config['BACKEND_DIR'], 'instance'), exist_ok=True)

    # init yolo service（放到 app.extensions，routes 里可直接拿）
    app.extensions['yolo'] = YoloService(Config.YOLOV5_PATH, Config.ROOT)

    # register blueprints
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(detect_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # init db & default admin
    with app.app_context():
        db.create_all()
        
        # 检查管理员用户是否存在
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("→ 创建默认管理员用户...")
            try:
                admin = User(username='admin', email='admin@example.com', is_admin=True)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print(f"✓ 管理员用户已创建: username=admin, email=admin@example.com, is_admin=True")
                
                # 验证管理员用户是否正确创建
                admin = User.query.filter_by(username='admin').first()
                if admin:
                    print(f"✓ 管理员用户验证成功: {admin.to_dict()}")
                else:
                    print(f"✗ 管理员用户验证失败")
            except Exception as e:
                print(f"✗ 创建管理员用户失败: {str(e)}")
                db.session.rollback()
        else:
            print(f"✓ 管理员用户已存在: {admin.to_dict()}")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=5001)