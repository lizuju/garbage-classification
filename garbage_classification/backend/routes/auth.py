from flask import Blueprint, jsonify, request, session

from ..extensions import db
from ..models import User
from ..services.log_service import log_action
from ..services.jwt_service import JWTManager, jwt_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    # 调试：打印请求信息
    print(f"Register - Content-Type: {request.content_type}")
    print(f"Register - Request data: {request.data}")
    
    # 尝试多种方式获取数据
    data = None
    
    # 方法1: 尝试解析JSON
    try:
        data = request.get_json(force=True, silent=True)
        print(f"Register - JSON data: {data}")
    except Exception as e:
        print(f"Register - JSON parse error: {e}")
    
    # 方法2: 如果JSON解析失败，尝试从form数据获取
    if not data:
        try:
            data = {
                'username': request.form.get('username'),
                'email': request.form.get('email'),
                'password': request.form.get('password')
            }
            print(f"Register - Form data: {data}")
        except Exception as e:
            print(f"Register - Form parse error: {e}")
    
    # 方法3: 如果都失败，尝试从原始数据解析
    if not data and request.data:
        try:
            import json
            data = json.loads(request.data.decode('utf-8'))
            print(f"Register - Raw data parsed: {data}")
        except Exception as e:
            print(f"Register - Raw data parse error: {e}")
    
    if not data:
        data = {}

    # 验证必要字段
    email = data.get('email', '').strip().lower()  # 邮箱转小写，统一处理
    password = data.get('password', '').strip()
    username = data.get('username', '').strip()
    
    # 如果没有username，用email作为username
    if not username and email:
        username = email.split('@')[0]
    
    if not email or not password or not username:
        return jsonify({
            'status': 'error', 
            'message': '缺少必要字段: email, password',
            'received': list(data.keys()) if data else '无数据',
            'content_type': request.content_type,
            'debug': {
                'is_json': request.is_json,
                'has_form': bool(request.form),
                'has_data': bool(request.data)
            }
        }), 400
    
    # 验证密码长度至少8个字符
    if len(password) < 8:
        return jsonify({
            'status': 'error', 
            'message': '密码长度至少为8个字符'
        }), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'status': 'error', 'message': '用户名已存在'}), 400

    # 检查邮箱是否已注册（使用小写比较防止大小写重复）
    existing_user = User.query.filter(User.email.ilike(email)).first()
    if existing_user:
        return jsonify({'status': 'error', 'message': '邮箱已被注册'}), 400

    user = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)
    try:
        db.session.commit()
        print(f"✓ 用户注册成功: {username} ({email})")
        
        # 注册成功后再记录，如果失败不影响注册结果
        try:
            log_action('user_action', f'用户注册: {username}')
        except Exception as log_err:
            print(f"日志记录失败: {log_err}")
        
        return jsonify({'status': 'success', 'message': '注册成功', 'user': user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        print(f"✗ 注册失败异常: {str(e)}")
        return jsonify({'status': 'error', 'message': f'注册失败: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    # 调试：打印请求信息
    print(f"Content-Type: {request.content_type}")
    print(f"Request data: {request.data}")
    print(f"Is JSON: {request.is_json}")
    
    # 尝试多种方式获取数据
    data = None
    
    # 方法1: 尝试解析JSON
    try:
        data = request.get_json(force=True, silent=True)
        print(f"JSON data: {data}")
    except Exception as e:
        print(f"JSON parse error: {e}")
    
    # 方法2: 如果JSON解析失败，尝试从form数据获取
    if not data:
        try:
            data = {
                'username': request.form.get('username'),
                'email': request.form.get('email'),
                'password': request.form.get('password')
            }
            print(f"Form data: {data}")
        except Exception as e:
            print(f"Form parse error: {e}")
    
    # 方法3: 如果都失败，尝试从原始数据解析
    if not data and request.data:
        try:
            import json
            data = json.loads(request.data.decode('utf-8'))
            print(f"Raw data parsed: {data}")
        except Exception as e:
            print(f"Raw data parse error: {e}")
    
    if not data:
        data = {}

    # 获取登陆凭证（可能是login_id、username或email）
    login_id = data.get('login_id') or data.get('username') or data.get('email')
    password = data.get('password', '')
    
    if not login_id or not password:
        return jsonify({
            'status': 'error', 
            'message': '缺少必要字段: login_id/username/email 和 password',
            'received': list(data.keys()) if data else '无数据'
        }), 400

    # 验证用户凭证
    try:
        # 尝试用 username 查询
        user = User.query.filter_by(username=login_id).first()
        
        # 如果没找到，尝试用 email 查询（邮箱需要小写比较）
        if not user:
            user = User.query.filter(User.email.ilike(login_id)).first()
        
        # 验证密码
        if user and user.check_password(password):
            if user.is_active is False:
                return jsonify({'status': 'error', 'message': '账号已被禁用'}), 403
            print(f"✓ 用户验证成功: {user.username} (is_admin={user.is_admin})")
            
            # 生成 JWT token
            token = JWTManager.encode_token(user.id, user.username, user.is_admin)
            
            if not token:
                return jsonify({'status': 'error', 'message': 'Token 生成失败'}), 500
            
            # 记录日志
            try:
                log_action('user_action', f'用户登录: {user.username}', user.id)
            except Exception as log_err:
                print(f"日志记录失败: {log_err}")
            
            # 返回用户数据和 token
            user_data = user.to_dict()
            return jsonify({
                'status': 'success',
                'message': '登录成功',
                'user': user_data,
                'token': token  # 前端需要保存这个 token
            }), 200
        else:
            print(f"✗ 登录失败: {login_id} - 用户名/邮箱或密码错误")
            return jsonify({'status': 'error', 'message': '用户名/邮箱或密码错误'}), 401
                
    except Exception as e:
        print(f"✗ 登录异常: {str(e)}")
        return jsonify({'status': 'error', 'message': f'登录失败: {str(e)}'}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    # JWT 方式无需做任何事，客户端删除 token 即可
    return jsonify({'status': 'success', 'message': '注销成功'}), 200


@auth_bp.route('/user', methods=['GET'])
@jwt_required
def get_user():
    """获取当前用户信息（使用 JWT 认证）"""
    payload = request.jwt_payload
    user_id = payload['user_id']
    
    try:
        user = User.query.get(user_id)
        
        if not user:
            print(f"✗ 用户不存在: {user_id}")
            return jsonify({'status': 'error', 'message': '用户不存在'}), 404
        
        user_data = user.to_dict()
        print(f"✓ 用户数据已返回: {user_data}")
        
        return jsonify({'status': 'success', 'user': user_data}), 200
        
    except Exception as e:
        print(f"✗ 获取用户信息失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '获取用户信息失败'}), 500
