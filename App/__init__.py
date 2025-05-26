# app/__init__.py

from flask import Flask
from flask_cors import CORS
from .config import Config
from .routes import register_blueprints
from .utils import create_upload_dir
from .utils import Logger

app_logger = Logger(name="APP", enable_file=True)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    app.logger_custom = app_logger
    create_upload_dir(app)
    register_blueprints(app)
    app_logger.info("应用初始化完成")

    return app
