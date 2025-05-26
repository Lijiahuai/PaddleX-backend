# app/config.py

import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploaded_files')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
    MODEL_FOLDER = os.path.join(BASE_DIR, 'models')

    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'txt', 'csv', 'mp4',
                          'wav', 'mp3', 'docx', 'doc', 'pdf'}

    DEBUG = True
