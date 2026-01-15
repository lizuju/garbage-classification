from flask import Blueprint, render_template

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

