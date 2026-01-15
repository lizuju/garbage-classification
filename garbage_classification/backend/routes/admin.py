import json
from datetime import datetime

from flask import Blueprint, jsonify, request

from ..models import User, Image, SystemLog
from ..services.auth_service import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/users')
@admin_required
def list_users():
    users = User.query.all()
    user_list = [user.to_dict() for user in users]
    return jsonify({'status': 'success', 'users': user_list}), 200


@admin_bp.route('/admin/logs')
@admin_required
def list_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    logs_query = SystemLog.query.order_by(SystemLog.created_at.desc())
    pagination = logs_query.paginate(page=page, per_page=per_page, error_out=False)

    logs = []
    for log in pagination.items:
        log_dict = {
            'id': log.id,
            'log_type': log.log_type,
            'message': log.message,
            'user_id': log.user_id,
            'created_at': log.created_at.isoformat()
        }
        if log.user_id:
            user = User.query.get(log.user_id)
            if user:
                log_dict['username'] = user.username
        logs.append(log_dict)

    return jsonify({
        'status': 'success',
        'logs': logs,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@admin_bp.route('/admin/stats')
@admin_required
def get_stats():
    total_users = User.query.count()
    new_users_today = User.query.filter(
        User.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()

    total_images = Image.query.count()
    images_today = Image.query.filter(
        Image.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()

    class_names = ['可回收', '有害', '厨余', '其他']
    class_counts = {name: 0 for name in class_names}
    for image in Image.query.all():
        if image.result_data:
            try:
                results = json.loads(image.result_data)
                for result in results:
                    class_name = result.get('class_name')
                    if class_name in class_counts:
                        class_counts[class_name] += 1
            except Exception:
                pass

    return jsonify({
        'status': 'success',
        'users': {'total': total_users, 'new_today': new_users_today},
        'images': {'total': total_images, 'new_today': images_today},
        'classes': class_counts
    }), 200

