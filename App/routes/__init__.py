# app/routes/__init__.py

from .image_interface import image_bp
from .audio_interface import audio_bp
from .text_interface import text_bp
from .video_interface import video_bp
from .upload_interface import upload_bp


def register_blueprints(app):
    app.register_blueprint(image_bp)
    app.register_blueprint(audio_bp)
    app.register_blueprint(text_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(upload_bp)
