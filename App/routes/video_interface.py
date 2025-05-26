# routes/video.py
from flask import Blueprint, request, jsonify
from App.services.video_service import VideoService

video_bp = Blueprint('video', __name__, url_prefix='/video')
video_service = VideoService()


@video_bp.route('/analyse', methods=['POST'])
def process_video():
    """视频处理基础接口"""
    try:
        data = request.get_json()
        file_id = data['file_Ids']
        result = video_service.video_analyse(file_id[0])

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except FileNotFoundError as e:
        return jsonify({"status": "failed", "error": str(e)}), 404
    except Exception as e:
        return jsonify({"status": "failed", "error": f"视频处理异常: {str(e)}"}), 500


@video_bp.route('/extract_frames', methods=['POST'])
def extract_frames():
    """关键帧提取接口"""
    try:
        data = request.get_json()
        file_id = data['file_id']
        interval = data.get('interval', 5)  # 默认每5秒提取一帧
        result = video_service.extract_key_frames(file_id, interval)

        return jsonify({
            "status": "success",
            "frame_count": len(result),
            "frames": result
        }), 200

    except FileNotFoundError as e:
        return jsonify({"status": "failed", "error": str(e)}), 404
    except Exception as e:
        return jsonify({"status": "failed", "error": f"关键帧提取失败: {str(e)}"}), 500


@video_bp.route('/generate_thumbnail', methods=['POST'])
def generate_thumbnail():
    """生成视频缩略图接口"""
    try:
        data = request.get_json()
        file_id = data['file_id']
        timestamp = data.get('timestamp', 0)  # 默认取首帧
        result = video_service.generate_thumbnail(file_id, timestamp)

        return jsonify({
            "status": "success",
            "thumbnail_url": result
        }), 200

    except FileNotFoundError as e:
        return jsonify({"status": "failed", "error": str(e)}), 404
    except Exception as e:
        return jsonify({"status": "failed", "error": f"缩略图生成失败: {str(e)}"}), 500
