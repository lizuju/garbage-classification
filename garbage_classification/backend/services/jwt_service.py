import jwt
import time
from functools import wraps
from flask import request, jsonify
from ..config import Config
from ..models import User


class JWTManager:
    """JWT token 管理器"""

    @staticmethod
    def encode_token(user_id, username, is_admin=False, expires_in=None):
        """
        编码 JWT token
        
        Args:
            user_id: 用户ID
            username: 用户名
            is_admin: 是否管理员
            
        Returns:
            str: JWT token
        """
        expiration = expires_in if expires_in is not None else Config.JWT_EXPIRATION
        payload = {
            'user_id': user_id,
            'username': username,
            'is_admin': is_admin,
            'iat': time.time(),
            'exp': time.time() + expiration,
        }
        
        try:
            token = jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')
            print(f"✓ Token 已生成: user_id={user_id}, username={username}, is_admin={is_admin}")
            return token
        except Exception as e:
            print(f"✗ Token 生成失败: {str(e)}")
            return None

    @staticmethod
    def decode_token(token):
        """
        解码 JWT token
        
        Args:
            token: JWT token字符串
            
        Returns:
            dict: 解码后的 payload，失败返回 None
        """
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            print(f"✗ Token 已过期")
            return None
        except jwt.InvalidTokenError as e:
            print(f"✗ Token 无效: {str(e)}")
            return None

    @staticmethod
    def get_token_from_request():
        """
        从请求头中获取 token
        
        Returns:
            str: token，或 None
        """
        auth_header = request.headers.get('Authorization', '')
        
        # 支持 "Bearer <token>" 格式
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        return None


def jwt_required(f):
    """
    JWT 认证装饰器
    
    用法：
        @app.route('/api/user')
        @jwt_required
        def get_user():
            payload = request.jwt_payload
            user_id = payload['user_id']
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = JWTManager.get_token_from_request()
        
        if not token:
            return jsonify({'status': 'error', 'message': '缺少认证令牌'}), 401
        
        payload = JWTManager.decode_token(token)
        
        if not payload:
            return jsonify({'status': 'error', 'message': '认证令牌无效或已过期'}), 401
        
        # 校验用户状态（是否存在/是否被禁用）
        user = User.query.get(payload.get('user_id'))
        if not user:
            return jsonify({'status': 'error', 'message': '用户不存在'}), 404
        if user.is_active is False:
            return jsonify({'status': 'error', 'message': '账号已被禁用'}), 403

        # 将 payload 附加到请求对象上，供路由函数使用
        request.jwt_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """
    需要管理员权限的装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = JWTManager.get_token_from_request()
        
        if not token:
            return jsonify({'status': 'error', 'message': '缺少认证令牌'}), 401
        
        payload = JWTManager.decode_token(token)
        
        if not payload:
            return jsonify({'status': 'error', 'message': '认证令牌无效或已过期'}), 401
        
        # 校验用户状态（是否存在/是否被禁用）
        user = User.query.get(payload.get('user_id'))
        if not user:
            return jsonify({'status': 'error', 'message': '用户不存在'}), 404
        if user.is_active is False:
            return jsonify({'status': 'error', 'message': '账号已被禁用'}), 403

        if not payload.get('is_admin'):
            return jsonify({'status': 'error', 'message': '需要管理员权限'}), 403
        
        request.jwt_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated_function
