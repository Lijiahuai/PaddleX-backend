# app/utils.py

import os
import uuid
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png'}


def create_upload_dir(app):
    folders = [
        app.config['UPLOAD_FOLDER'],
        app.config['OUTPUT_FOLDER'],
        app.config['MODEL_FOLDER']
    ]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"[INFO] Created folder: {folder}")


def is_allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, session_id):
    if file.filename == '':
        raise ValueError("空文件名")

    if not is_allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        raise ValueError(f"文件类型不支持: {file.filename}")

    ext = file.filename.rsplit('.', 1)[-1].lower()
    if not ext:
        raise ValueError("无效扩展名")

    # 当前日期文件夹
    date_folder = datetime.now().strftime('%Y-%m-%d')
    base_path = os.path.join(current_app.config['UPLOAD_FOLDER'], date_folder, session_id)
    os.makedirs(base_path, exist_ok=True)

    # 如果是图像文件，重命名为 UUID
    if ext in IMAGE_EXTENSIONS:
        filename = f"{uuid.uuid4().hex}.{ext}"
    else:
        filename = secure_filename(file.filename)

    save_path = os.path.join(base_path, filename)

    try:
        with open(save_path, 'wb') as f:
            file.save(f)
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        raise IOError(f"文件保存失败: {str(e)}")

    return os.path.abspath(save_path)


class Logger:
    def __init__(self, name="APP", enable_file=False, log_dir="logs"):
        self.name = name
        self.enable_file = enable_file
        self.log_dir = log_dir

        if self.enable_file and not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def _get_time(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _format_msg(self, level, message):
        return f"[{self._get_time()}] [{self.name}] [{level}] {message}"

    def _write_to_file(self, msg):
        if not self.enable_file:
            return
        log_file = os.path.join(self.log_dir, f"{self.name.lower()}.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    def info(self, message):
        msg = self._format_msg("INFO", message)
        print(msg)
        self._write_to_file(msg)

    def warn(self, message):
        msg = self._format_msg("WARN", message)
        print(msg)
        self._write_to_file(msg)

    def error(self, message):
        msg = self._format_msg("ERROR", message)
        print(msg)
        self._write_to_file(msg)

    def debug(self, message):
        msg = self._format_msg("DEBUG", message)
        print(msg)
        self._write_to_file(msg)
