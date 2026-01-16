from flask import Blueprint, jsonify, request, session

from ..extensions import db
from ..models import User
from ..services.log_service import log_action
from ..services.auth_service import AuthManager

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

    # 获取登陆凭证（可能是username或email）
    login_id = data.get('username') or data.get('email')
    password = data.get('password', '')
    
    if not login_id or not password:
        return jsonify({
            'status': 'error', 
            'message': '缺少必要字段: username/email 和 password',
            'received': list(data.keys()) if data else '无数据'
        }), 400

    # 使用 AuthManager 验证用户
    user = AuthManager.verify_user_by_credentials(login_id, password)
    
    if user:
        # 创建会话
        if AuthManager.create_session(user):
            # 记录日志
            try:
                log_action('user_action', f'用户登录: {user.username}', user.id)
            except Exception as log_err:
                print(f"日志记录失败: {log_err}")
            
            # 返回用户数据
            user_data = AuthManager.get_user_data(user)
            return jsonify({'status': 'success', 'message': '登录成功', 'user': user_data}), 200
        else:
            return jsonify({'status': 'error', 'message': '会话创建失败，请重试'}), 500
    else:
        print(f"✗ 登录失败: {login_id} - 用户名/邮箱或密码错误")
        return jsonify({'status': 'error', 'message': '用户名/邮箱或密码错误'}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout():
    # 获取当前用户，用于日志记录
    user = AuthManager.get_current_user()
    if user:
        try:
            log_action('user_action', f'用户登出: {user.username}', user.id)
        except Exception as log_err:
            print(f"日志记录失败: {log_err}")
    
    # 销毁会话
    AuthManager.destroy_session()
    
    return jsonify({'status': 'success', 'message': '注销成功'}), 200


@auth_bp.route('/user', methods=['GET'])
def get_user():
    print(f"→ 检查用户状态: session={dict(session)}")
    
    # 使用 AuthManager 获取当前用户
    user = AuthManager.get_current_user()
    
    if not user:
        print(f"✗ 未登录或用户不存在")
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 获取用户数据
    user_data = AuthManager.get_user_data(user)
    
    if not user_data:
        print(f"✗ 用户数据生成失败")
        return jsonify({'status': 'error', 'message': '用户数据获取失败'}), 500
    
    response = jsonify({'status': 'success', 'user': user_data})
    print(f"✓ 响应头: {dict(response.headers)}")
    return response, 200

