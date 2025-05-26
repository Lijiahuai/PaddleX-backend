import uuid
from flask import Blueprint, request, jsonify, current_app
from App.utils import create_upload_dir, save_uploaded_file

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/api/upload', methods=['POST'])
def upload_files():
    current_app.logger_custom.info("收到 /api/upload 上传请求")
    create_upload_dir(current_app)

    if 'files' not in request.files:
        current_app.logger_custom.warning("上传失败：未选择文件")
        return jsonify({"error": "未选择文件"}), 400

    files = request.files.getlist('files')
    filenames = [f.filename for f in files if f.filename]
    if not files or all(f.filename == '' for f in files):
        current_app.logger_custom.warning("上传失败：空文件名")
        return jsonify({"error": "空文件名"}), 400

    current_app.logger_custom.info(f"准备上传文件列表：{filenames}")

    session_id = uuid.uuid4().hex
    saved_paths = []
    errors = []

    for file in files:
        try:
            path = save_uploaded_file(file, session_id)
            saved_paths.append(path)
            current_app.logger_custom.info(f"保存文件成功：{file.filename} -> {path}")
        except Exception as e:
            error_msg = f"{file.filename}: {str(e)}"
            errors.append(error_msg)
            current_app.logger_custom.error(f"保存文件失败：{error_msg}")

    if not saved_paths:
        current_app.logger_custom.error(f"所有文件上传失败，详情：{errors}")
        return jsonify({"success": False, "error": "所有文件上传失败", "details": errors}), 500

    current_app.logger_custom.info(f"上传完成，成功数量：{len(saved_paths)}，失败数量：{len(errors)}")
    return jsonify({
        "success": True,
        "paths": saved_paths,
        "count": len(saved_paths),
        "errors": errors if errors else None
    }), 200
