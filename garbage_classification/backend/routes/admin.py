from flask import Blueprint, jsonify, request

from ..services.jwt_service import admin_required
from ..services.admin_service import admin_service
from ..services.log_service import log_action
from ..extensions import db
from ..models import User

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/users')
@admin_required
def list_users():
    user_list = admin_service.get_users_list()
    return jsonify({'status': 'success', 'users': user_list}), 200

def _admin_count():
    return User.query.filter_by(is_admin=True).count()


@admin_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_detail(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    return jsonify({'status': 'success', 'user': user.to_dict()}), 200


@admin_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user_detail(user_id):
    data = request.get_json() or {}
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404

    # 用户名更新
    if 'username' in data and data['username']:
        new_username = data['username'].strip()
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'status': 'error', 'message': '用户名已存在'}), 400
        user.username = new_username

    # 邮箱更新
    if 'email' in data and data['email']:
        new_email = data['email'].strip().lower()
        existing_user = User.query.filter(User.email.ilike(new_email)).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'status': 'error', 'message': '邮箱已被使用'}), 400
        user.email = new_email

    # 密码更新（可选）
    if 'new_password' in data and data['new_password']:
        new_pwd = data.get('new_password', '')
        confirm_pwd = data.get('confirm_password', '')
        if len(new_pwd) < 8:
            return jsonify({'status': 'error', 'message': '新密码长度至少 8 个字符'}), 400
        if user.check_password(new_pwd):
            return jsonify({'status': 'error', 'message': '新密码不能与当前密码相同'}), 400
        if new_pwd != confirm_pwd:
            return jsonify({'status': 'error', 'message': '两次输入的密码不一致'}), 400
        user.set_password(new_pwd)
    
    # 管理员标识更新（可选）
    if 'is_admin' in data:
        new_is_admin = bool(data['is_admin'])
        # 防止降级最后一个管理员
        if user.is_admin and not new_is_admin and _admin_count() <= 1:
            return jsonify({'status': 'error', 'message': '至少需要保留一个管理员账户'}), 400
        user.is_admin = new_is_admin

    # 用户状态更新（可选）
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])

    # 统一规则：管理员账号不可禁用
    if user.is_admin and user.is_active is False:
        return jsonify({'status': 'error', 'message': '管理员账户不能禁用'}), 400

    try:
        db.session.commit()
        log_action('admin_action', f'管理员更新用户资料: {user.username}', user.id)
        return jsonify({'status': 'success', 'message': '用户资料已更新', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500


@admin_bp.route('/admin/users/<int:user_id>/status', methods=['PATCH'])
@admin_required
def update_user_status(user_id):
    data = request.get_json() or {}
    if 'is_active' not in data:
        return jsonify({'status': 'error', 'message': '缺少 is_active 字段'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404

    # 不允许禁用管理员账户
    if user.is_admin and data.get('is_active') is False:
        return jsonify({'status': 'error', 'message': '管理员账户不能禁用'}), 400

    # 不允许禁用自己
    current_user_id = getattr(request, 'jwt_payload', {}).get('user_id')
    if user.id == current_user_id and data.get('is_active') is False:
        return jsonify({'status': 'error', 'message': '不能禁用当前登录管理员'}), 400

    user.is_active = bool(data.get('is_active'))

    try:
        db.session.commit()
        action = '恢复' if user.is_active else '禁用'
        log_action('admin_action', f'管理员{action}用户: {user.username}', user.id)
        return jsonify({'status': 'success', 'message': f'用户已{action}', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500

@admin_bp.route('/admin/logs')
@admin_required
def list_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    logs_data = admin_service.get_system_logs(page=page, per_page=per_page)
    
    return jsonify({
        'status': 'success',
        'logs': logs_data['items'],
        'total': logs_data['total'],
        'pages': logs_data['pages'],
        'current_page': logs_data['current_page']
    }), 200

@admin_bp.route('/admin/stats')
@admin_required
def get_stats():
    stats_data = admin_service.get_dashboard_stats()
    return jsonify({
        'status': 'success',
        'stats': stats_data
    }), 200

@admin_bp.route('/admin/export')
@admin_required
def export_data():
    data = admin_service.export_system_data()
    return jsonify({
        'status': 'success',
        'export_data': data
    }), 200
