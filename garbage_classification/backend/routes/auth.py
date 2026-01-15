from flask import Blueprint, jsonify, request, session

from ..extensions import db
from ..models import User
from ..services.log_service import log_action

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    if not all(field in data for field in ['username', 'email', 'password']):
        return jsonify({'status': 'error', 'message': '缺少必要字段'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'status': 'error', 'message': '用户名已存在'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'status': 'error', 'message': '邮箱已被注册'}), 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])

    db.session.add(user)
    try:
        db.session.commit()
        log_action('user_action', f'用户注册: {data["username"]}')
        return jsonify({'status': 'success', 'message': '注册成功', 'user': user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'注册失败: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    if not all(field in data for field in ['username', 'password']):
        return jsonify({'status': 'error', 'message': '缺少必要字段'}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        session['user_id'] = user.id
        log_action('user_action', f'用户登录: {user.username}', user.id)
        return jsonify({'status': 'success', 'message': '登录成功', 'user': user.to_dict()}), 200

    return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            log_action('user_action', f'用户登出: {user.username}', user_id)
    session.pop('user_id', None)
    return jsonify({'status': 'success', 'message': '注销成功'}), 200


@auth_bp.route('/user', methods=['GET'])
def get_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401

    user = db.session.get(User, user_id)
    if not user:
        session.pop('user_id', None)
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404

    return jsonify({'status': 'success', 'user': user.to_dict()}), 200

