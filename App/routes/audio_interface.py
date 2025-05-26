# routes/audio.py
from flask import Blueprint, request, jsonify
from flask import current_app
from App.services.audio_service import AudioService

audio_bp = Blueprint('audio', __name__, url_prefix='/audio')
audio_service = AudioService()


@audio_bp.route('/recognize', methods=['POST'])
def recognize():
    current_app.logger_custom.info("收到 /audio/recognize 请求")
    try:
        data = request.get_json()
        paths = data['paths']
        current_app.logger_custom.debug(f"语音识别文件路径列表: {paths}")

        result = audio_service.recognize_speech(paths)
        current_app.logger_custom.info(f"/audio/recognize 处理完成，返回 {len(result)} 条结果")

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except FileNotFoundError as e:
        current_app.logger_custom.error(f"/audio/recognize 文件未找到: {str(e)}")
        return jsonify({"status": "failed", "error": str(e)}), 404
    except Exception as e:
        current_app.logger_custom.error(f"/audio/recognize 处理异常: {str(e)}", exc_info=True)
        return jsonify({"status": "failed", "error": f"处理异常: {str(e)}"}), 500
