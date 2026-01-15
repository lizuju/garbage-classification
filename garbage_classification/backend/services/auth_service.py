from functools import wraps
from flask import jsonify, session

from ..models import User


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'status': 'error', 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'status': 'error', 'message': '请先登录'}), 401

        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'status': 'error', 'message': '需要管理员权限'}), 403

        return f(*args, **kwargs)
    return decorated_function

