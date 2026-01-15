import json
import os
import uuid

from flask import Blueprint, jsonify, request, send_file, current_app, session
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import Image, DetectionHistory, User
from ..services.auth_service import login_required
from ..services.log_service import log_action
from ..utils.file import allowed_file, resolve_stored_path

detect_bp = Blueprint('detect', __name__)


@detect_bp.route('/detect', methods=['POST'])
@login_required
def detect():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': '没有文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': '没有选择文件'}), 400

    if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        return jsonify({'status': 'error', 'message': f'只支持 {", ".join(current_app.config["ALLOWED_EXTENSIONS"])} 格式图像'}), 400

    try:
        file_bytes = file.read()

        filename = secure_filename(file.filename)
        unique_id = uuid.uuid4().hex
        unique_filename = f"{unique_id}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)

        with open(file_path, 'wb') as f:
            f.write(file_bytes)

        results, result_img = current_app.extensions['yolo'].detect(file_bytes)

        result_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'results', f"{unique_id}_result.jpg")
        if result_img is not None:
            result_img.save(result_path)

        result_json = json.dumps(results, ensure_ascii=False) if results else "[]"
        image = Image(
            filename=unique_filename,
            original_path=file_path,
            result_path=result_path,
            result_data=result_json,
            user_id=session['user_id']
        )
        db.session.add(image)

        confidence = max([item.get('confidence', 0) for item in results]) if results else 0
        history = DetectionHistory(
            user_id=session['user_id'],
            image_path=file_path,
            result=result_json,
            confidence=confidence
        )
        db.session.add(history)
        db.session.commit()

        log_action('user_action', f'Detection finished: {len(results)} objects', session['user_id'])

        return jsonify({
            'status': 'success',
            'image_id': image.id,
            'results': results,
            'original_url': f"/api/images/{image.id}/original",
            'result_url': f"/api/images/{image.id}/result",
            'history_id': history.id,
            'message': '识别完成' if results else '未检测到垃圾物品'
        }), 200

    except Exception as e:
        db.session.rollback()
        log_action('error', f'识别错误: {str(e)}', session.get('user_id'))
        return jsonify({'status': 'error', 'message': f'处理图像时出错: {str(e)}'}), 500


@detect_bp.route('/images/<int:image_id>/original')
@login_required
def get_original_image(image_id):
    image = Image.query.get_or_404(image_id)

    if image.user_id != session['user_id'] and not User.query.get(session['user_id']).is_admin:
        return jsonify({'status': 'error', 'message': '无权访问此图像'}), 403

    resolved = resolve_stored_path(
        image.original_path,
        project_root=current_app.config['PROJECT_ROOT'],
        backend_dir=current_app.config['BACKEND_DIR']
    )
    if not resolved:
        return jsonify({'status': 'error', 'message': '原始图片文件不存在或路径无效'}), 404
    return send_file(resolved)


@detect_bp.route('/images/<int:image_id>/result')
@login_required
def get_result_image(image_id):
    image = Image.query.get_or_404(image_id)

    if image.user_id != session['user_id'] and not User.query.get(session['user_id']).is_admin:
        return jsonify({'status': 'error', 'message': '无权访问此图像'}), 403

    resolved = resolve_stored_path(
        image.result_path,
        project_root=current_app.config['PROJECT_ROOT'],
        backend_dir=current_app.config['BACKEND_DIR']
    )
    if not resolved:
        return jsonify({'status': 'error', 'message': '结果图片文件不存在或尚未生成'}), 404
    return send_file(resolved)

