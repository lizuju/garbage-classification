from flask import Blueprint, jsonify, request

from ..services.jwt_service import admin_required
from ..services.admin_service import admin_service

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/users')
@admin_required
def list_users():
    user_list = admin_service.get_users_list()
    return jsonify({'status': 'success', 'users': user_list}), 200

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
