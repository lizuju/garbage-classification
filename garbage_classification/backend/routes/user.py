import json

from flask import Blueprint, jsonify, request

from ..models import User, Image, DetectionHistory
from ..extensions import db
from ..services.jwt_service import jwt_required
from ..services.log_service import log_action

user_bp = Blueprint('user', __name__)


@user_bp.route('/user/profile', methods=['GET', 'PUT'])
@jwt_required
def user_profile():
    payload = request.jwt_payload
    user_id = payload['user_id']
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    if request.method == 'GET':
        return jsonify({'status': 'success', 'user': user.to_dict()}), 200
    
    # PUT 请求处理
    data = request.get_json() or {}
    
    # 验证当前密码
    if 'password' not in data:
        return jsonify({'status': 'error', 'message': '需要提供当前密码进行验证'}), 400
    
    if not user.check_password(data['password']):
        return jsonify({'status': 'error', 'message': '当前密码错误'}), 401
    
    # 更新邮箱（可选）
    if 'email' in data:
        # 检查邮箱是否已被使用
        existing_user = User.query.filter(User.email.ilike(data['email'])).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'status': 'error', 'message': '邮箱已被使用'}), 400
        user.email = data['email'].lower()
    
    # 更新密码（可选）
    if 'new_password' in data and data['new_password']:
        # 1. 获取新密码和确认密码
        current_pwd = data.get('password')
        new_pwd = data.get('new_password')
        confirm_pwd = data.get('confirm_password')
        # 2. 校验长度
        if len(new_pwd) < 8:
            return jsonify({'status': 'error', 'message': '新密码长度至少 8 个字符'}), 400
        # 3. 校验新旧密码是否相同
        if current_pwd == new_pwd:
            return jsonify({'status': 'error', 'message': '新密码不能与当前密码相同'}), 400
        # 4. 校验一致性
        if new_pwd != confirm_pwd:
            return jsonify({'status': 'error', 'message': '两次输入的密码不一致'}), 400
        user.set_password(new_pwd)
    
    try:
        db.session.commit()
        log_action('user_action', '用户更新资料', user.id)
        return jsonify({'status': 'success', 'message': '资料已更新', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500


@user_bp.route('/user/history', methods=['GET'])
@jwt_required
def get_user_history():
    payload = request.jwt_payload
    user_id = payload['user_id']
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    history_query = DetectionHistory.query.filter_by(user_id=user_id).order_by(DetectionHistory.created_at.desc())
    pagination = history_query.paginate(page=page, per_page=page_size, error_out=False)

    history_list = []
    for record in pagination.items:
        try:
            results = json.loads(record.result) if record.result else []
            detection_count = len(results)
            
            history_list.append({
                'id': record.id,
                'detection_count': detection_count,
                'confidence': record.confidence,
                'created_at': record.created_at.isoformat() if record.created_at else '',
            })
        except Exception as e:
            print(f"Error processing history {record.id}: {str(e)}")
            pass

    return jsonify({
        'status': 'success',
        'data': history_list,
        'pagination': {
            'page': page,
            'per_page': page_size,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@user_bp.route('/user/history/<int:history_id>', methods=['DELETE'])
@jwt_required
def delete_user_history(history_id):
    payload = request.jwt_payload
    user_id = payload['user_id']
    
    record = DetectionHistory.query.get(history_id)
    
    if not record:
        return jsonify({'status': 'error', 'message': '历史记录不存在'}), 404
    
    if record.user_id != user_id:
        return jsonify({'status': 'error', 'message': '无权删除此记录'}), 403
    
    try:
        db.session.delete(record)
        db.session.commit()
        log_action('user_action', '用户删除历史记录', user_id)
        return jsonify({'status': 'success', 'message': '历史记录已删除'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500

