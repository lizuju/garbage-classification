from functools import wraps
from flask import jsonify, session

from ..models import User
from ..extensions import db


class AuthManager:
    """
    认证管理器 - 统一处理所有用户认证相关操作
    支持普通用户和管理员的无差别处理
    """

    @staticmethod
    def get_current_user():
        """
        获取当前登录用户
        
        Returns:
            User: 当前用户对象，如果未登录返回 None
        """
        user_id = session.get('user_id')
        if not user_id:
            return None
        
        try:
            # 使用 query.get() 而不是 db.session.get()，确保兼容性
            user = User.query.get(user_id)
            
            # 验证用户有效性
            if user and user.is_valid_for_session():
                return user
            
            # 如果用户无效，清除会话
            if user_id in session:
                session.pop('user_id', None)
            
            return None
        except Exception as e:
            print(f"✗ 获取当前用户异常: {str(e)}")
            return None

    @staticmethod
    def create_session(user):
        """
        创建用户会话
        
        Args:
            user (User): 用户对象
            
        Returns:
            bool: 会话创建是否成功
        """
        if not user or not user.is_valid_for_session():
            print(f"✗ 无效的用户对象，无法创建会话")
            return False
        
        try:
            session['user_id'] = user.id
            # 确保会话永久化
            session.permanent = True
            
            print(f"✓ 会话已创建: user_id={user.id}, username={user.username}, is_admin={user.is_admin}")
            print(f"✓ 当前会话: {dict(session)}")
            
            return True
        except Exception as e:
            print(f"✗ 创建会话异常: {str(e)}")
            return False

    @staticmethod
    def destroy_session():
        """
        销毁用户会话
        
        Returns:
            bool: 会话销毁是否成功
        """
        try:
            user_id = session.get('user_id')
            if user_id:
                print(f"✓ 销毁会话: user_id={user_id}")
            
            session.pop('user_id', None)
            return True
        except Exception as e:
            print(f"✗ 销毁会话异常: {str(e)}")
            return False

    @staticmethod
    def get_user_data(user):
        """
        获取用户数据
        
        Args:
            user (User): 用户对象
            
        Returns:
            dict: 用户数据字典
        """
        if not user:
            return None
        
        try:
            user_data = user.to_dict()
            print(f"✓ 用户数据已生成: {user_data}")
            return user_data
        except Exception as e:
            print(f"✗ 生成用户数据异常: {str(e)}")
            return None

    @staticmethod
    def verify_user_by_credentials(login_id, password):
        """
        通过凭证验证用户
        
        Args:
            login_id (str): 用户名或邮箱
            password (str): 密码
            
        Returns:
            User: 验证成功的用户对象，失败返回 None
        """
        if not login_id or not password:
            print(f"✗ 无效的登陆凭证")
            return None
        
        try:
            # 尝试用 username 查询
            user = User.query.filter_by(username=login_id).first()
            
            # 如果没找到，尝试用 email 查询（邮箱需要小写比较）
            if not user:
                user = User.query.filter(User.email.ilike(login_id)).first()
            
            # 验证密码
            if user and user.check_password(password):
                print(f"✓ 用户验证成功: {user.username} (is_admin={user.is_admin})")
                return user
            else:
                print(f"✗ 用户验证失败: {login_id}")
                return None
                
        except Exception as e:
            print(f"✗ 用户验证异常: {str(e)}")
            return None

    @staticmethod
    def check_permission(user, required_admin=False):
        """
        检查用户权限
        
        Args:
            user (User): 用户对象
            required_admin (bool): 是否需要管理员权限
            
        Returns:
            bool: 权限检查是否通过
        """
        if not user:
            return False
        
        if required_admin and not user.is_admin:
            print(f"✗ 权限不足: 用户 {user.username} 不是管理员")
            return False
        
        print(f"✓ 权限检查通过: {user.username}")
        return True


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = AuthManager.get_current_user()
        if not user:
            return jsonify({'status': 'error', 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = AuthManager.get_current_user()
        if not user or not user.is_admin:
            return jsonify({'status': 'error', 'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function

