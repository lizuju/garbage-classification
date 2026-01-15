import json

from flask import Blueprint, jsonify, request, session

from ..models import User, Image
from ..extensions import db
from ..services.auth_service import login_required
from ..services.log_service import log_action

user_bp = Blueprint('user', __name__)


@user_bp.route('/user/profile')
@login_required
def get_user_profile():
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    return jsonify({'status': 'success', 'user': user.to_dict()}), 200


@user_bp.route('/user/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json() or {}
    if not all(field in data for field in ['old_password', 'new_password']):
        return jsonify({'status': 'error', 'message': '缺少必要字段'}), 400

    user = User.query.get(session['user_id'])
    if not user.check_password(data['old_password']):
        return jsonify({'status': 'error', 'message': '旧密码不正确'}), 401

    user.set_password(data['new_password'])
    db.session.commit()
    log_action('user_action', '用户修改密码', user.id)
    return jsonify({'status': 'success', 'message': '密码已更新'}), 200


@user_bp.route('/user/history')
@login_required
def get_user_history():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    history_query = Image.query.filter_by(user_id=session['user_id']).order_by(Image.created_at.desc())
    pagination = history_query.paginate(page=page, per_page=per_page, error_out=False)

    history_list = []
    for image in pagination.items:
        try:
            results = json.loads(image.result_data) if image.result_data else []
            history_list.append({
                'id': image.id,
                'filename': image.filename,
                'results': results,
                'created_at': image.created_at.isoformat(),
                'original_url': f"/api/images/{image.id}/original",
                'result_url': f"/api/images/{image.id}/result"
            })
        except Exception:
            pass

    return jsonify({
        'status': 'success',
        'history': history_list,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

