import json
import os
import uuid

from flask import Blueprint, jsonify, request, send_file, current_app
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import Image, DetectionHistory, User
from ..services.jwt_service import jwt_required
from ..services.log_service import log_action
from ..utils.file import allowed_file, resolve_stored_path

detect_bp = Blueprint('detect', __name__)
MAX_BATCH_FILES = 20
MAX_SINGLE_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def _build_file_error(message, filename=''):
    return {
        'status': 'error',
        'filename': filename,
        'message': message
    }


def _validate_image_file(file_obj):
    if file_obj is None:
        return '没有文件'
    if not file_obj.filename:
        return '没有选择文件'
    if not allowed_file(file_obj.filename, current_app.config['ALLOWED_EXTENSIONS']):
        return f'只支持 {", ".join(current_app.config["ALLOWED_EXTENSIONS"])} 格式图像'
    try:
        pos = file_obj.stream.tell()
        file_obj.stream.seek(0, os.SEEK_END)
        size = file_obj.stream.tell()
        file_obj.stream.seek(pos)
        if size > MAX_SINGLE_FILE_SIZE:
            return '单张图片不能超过 5MB'
    except Exception:
        # ignore stream size read errors and let downstream handle
        pass
    return None


def _detect_one_file(file_obj, user):
    file_bytes = file_obj.read()
    if not file_bytes:
        raise ValueError('文件为空或读取失败')

    filename = secure_filename(file_obj.filename)
    unique_id = uuid.uuid4().hex
    unique_filename = f"{unique_id}_{filename}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)

    with open(file_path, 'wb') as f:
        f.write(file_bytes)

    results, result_img = current_app.extensions['yolo'].detect(file_bytes)

    result_path = None
    if result_img is not None:
        result_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'results', f"{unique_id}_result.jpg")
        result_img.save(result_path)

    result_json = json.dumps(results, ensure_ascii=False) if results else "[]"

    image = Image(
        filename=unique_filename,
        original_path=file_path,
        result_path=result_path,
        result_data=result_json,
        user_id=user.id
    )
    db.session.add(image)
    db.session.flush()

    history_id = None
    average_confidence = 0

    if results:
        confidences = [item.get('confidence', 0) for item in results]
        average_confidence = (sum(confidences) / len(confidences)) if confidences else 0
        history = DetectionHistory(
            user_id=user.id,
            image_path=file_path,
            result=result_json,
            confidence=average_confidence
        )
        db.session.add(history)
        db.session.flush()
        history_id = history.id
        log_action('user_action', f'检测完成：共 {len(results)} 个目标', user.id)

    db.session.commit()

    return {
        'status': 'success',
        'filename': file_obj.filename,
        'image_id': image.id,
        'results': results,
        'average_confidence': average_confidence,
        'original_url': f"/api/images/{image.id}/original",
        'result_url': f"/api/images/{image.id}/result",
        'history_id': history_id,
        'message': '识别完成' if results else '未检测到垃圾物品'
    }


@detect_bp.route('/detect', methods=['POST'])
@jwt_required
def detect():
    payload = request.jwt_payload
    user_id = payload['user_id']
    file_obj = request.files.get('file')
    validation_error = _validate_image_file(file_obj)
    if validation_error:
        return jsonify({'status': 'error', 'message': validation_error}), 400

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'status': 'error', 'message': '用户不存在'}), 404
        result = _detect_one_file(file_obj, user)
        return jsonify(result), 200

    except Exception as e:
        db.session.rollback()
        print(f"✗ 识别错误: {str(e)}")
        log_action('error', f'识别错误: {str(e)}', user_id)
        return jsonify({'status': 'error', 'message': f'处理图像时出错: {str(e)}'}), 500


@detect_bp.route('/detect/batch', methods=['POST'])
@jwt_required
def detect_batch():
    payload = request.jwt_payload
    user_id = payload['user_id']

    files = request.files.getlist('files')
    if not files:
        files = request.files.getlist('file')
    files = [f for f in files if f and f.filename]

    if not files:
        return jsonify({'status': 'error', 'message': '没有选择文件'}), 400

    if len(files) > MAX_BATCH_FILES:
        return jsonify({
            'status': 'error',
            'message': f'单次最多上传 {MAX_BATCH_FILES} 张图片'
        }), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404

    items = []
    success_count = 0

    for file_obj in files:
        validation_error = _validate_image_file(file_obj)
        if validation_error:
            items.append(_build_file_error(validation_error, file_obj.filename))
            continue

        try:
            result = _detect_one_file(file_obj, user)
            items.append(result)
            success_count += 1
        except Exception as e:
            db.session.rollback()
            print(f"✗ 批量识别错误({file_obj.filename}): {str(e)}")
            log_action('error', f'批量识别错误({file_obj.filename}): {str(e)}', user_id)
            items.append(_build_file_error(f'处理图像时出错: {str(e)}', file_obj.filename))

    failed_count = len(files) - success_count
    if success_count == 0:
        return jsonify({
            'status': 'error',
            'message': '批量识别失败',
            'total': len(files),
            'success_count': success_count,
            'failed_count': failed_count,
            'items': items
        }), 400

    return jsonify({
        'status': 'success',
        'message': f'批量识别完成：成功 {success_count} 张，失败 {failed_count} 张',
        'total': len(files),
        'success_count': success_count,
        'failed_count': failed_count,
        'items': items
    }), 200


@detect_bp.route('/images/<int:image_id>/original')
@jwt_required
def get_original_image(image_id):
    payload = request.jwt_payload
    user_id = payload['user_id']
    
    image = Image.query.get_or_404(image_id)

    user = User.query.get(user_id)
    if not user or (image.user_id != user.id and not user.is_admin):
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
@jwt_required
def get_result_image(image_id):
    payload = request.jwt_payload
    user_id = payload['user_id']
    
    image = Image.query.get_or_404(image_id)

    user = User.query.get(user_id)
    if not user or (image.user_id != user.id and not user.is_admin):
        return jsonify({'status': 'error', 'message': '无权访问此图像'}), 403

    resolved = resolve_stored_path(
        image.result_path,
        project_root=current_app.config['PROJECT_ROOT'],
        backend_dir=current_app.config['BACKEND_DIR']
    )
    if not resolved:
        return jsonify({'status': 'error', 'message': '结果图片文件不存在或尚未生成'}), 404
    return send_file(resolved)
