from flask import Blueprint, render_template

from ..services.auth_service import login_required

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def index():
    return render_template('index.html')


@pages_bp.route('/login')
def login_page():
    return render_template('login.html')


@pages_bp.route('/register')
def register_page():
    return render_template('register.html')


@pages_bp.route('/detect')
def detect_page():
    return render_template('detect.html')


@pages_bp.route('/history')
def history_page():
    return render_template('history.html')


@pages_bp.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html')


@pages_bp.route('/about')
def about_page():
    return render_template('about.html')

