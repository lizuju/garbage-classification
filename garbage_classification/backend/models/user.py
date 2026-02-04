from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, email, **kwargs):
        super().__init__(username=username, email=email.lower(), **kwargs)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """
        转换用户对象为字典
        支持所有用户类型（包括管理员）的序列化
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': bool(self.is_admin),  # 显式转换为 bool，确保管理员标志正确
            'created_at': (self.created_at.isoformat() + 'Z') if self.created_at else None
        }
    
    def is_valid_for_session(self):
        """
        验证用户是否可以建立会话
        确保用户数据的完整性
        """
        return (self.id is not None and 
                self.username is not None and 
                self.email is not None)

