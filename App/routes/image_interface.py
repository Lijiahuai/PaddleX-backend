# routes/image.py
import os

from flask import Blueprint, send_from_directory
from flask import request, jsonify, current_app
from App.services.image_service import ImageService

# 创建蓝图，设置URL前缀为/image
image_bp = Blueprint('image', __name__, url_prefix='/image')
image_service = ImageService()


from flask import current_app

@image_bp.route('/recognize', methods=['POST'])
def image_recognize():
    current_app.logger_custom.info("收到 /image/recognize 请求")
    try:
        data = request.get_json()
        paths = data['paths']
        current_app.logger_custom.debug(f"识别路径列表: {paths}")

        result = image_service.process_ocr(paths)
        current_app.logger_custom.info(f"/image/recognize 处理完成，返回 {len(result)} 条结果")

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except FileNotFoundError as e:
        current_app.logger_custom.error(f"/image/recognize 文件未找到: {str(e)}")
        return jsonify({"status": "failed", "error": str(e)}), 404
    except Exception as e:
        current_app.logger_custom.error(f"/image/recognize 处理异常: {str(e)}", exc_info=True)
        return jsonify({"status": "failed", "error": f"处理异常: {str(e)}"}), 500


@image_bp.route('/table', methods=['POST'])
def table_recognize():
    current_app.logger_custom.info("收到 /image/table 请求")
    try:
        data = request.get_json()
        paths = data['paths']
        current_app.logger_custom.debug(f"表格识别路径列表: {paths}")

        result = image_service.process_table_recognise(paths)
        current_app.logger_custom.info(f"/image/table 处理完成，返回 {len(result)} 条结果")

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except FileNotFoundError as e:
        current_app.logger_custom.error(f"/image/table 文件未找到: {str(e)}")
        return jsonify({"status": "failed", "error": str(e)}), 404
    except Exception as e:
        current_app.logger_custom.error(f"/image/table 处理异常: {str(e)}", exc_info=True)
        return jsonify({"status": "failed", "error": f"处理异常: {str(e)},该图片可能不包含表格。"}), 500


@image_bp.route('/seal', methods=['POST'])
def seal_recognize():
    current_app.logger_custom.info("收到 /image/seal 请求")
    try:
        data = request.get_json()
        paths = data['paths']
        current_app.logger_custom.debug(f"印章识别路径列表: {paths}")

        result = image_service.process_seal_recognise(paths)
        current_app.logger_custom.info(f"/image/seal 处理完成，返回 {len(result)} 条结果")

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except FileNotFoundError as e:
        current_app.logger_custom.error(f"/image/seal 文件未找到: {str(e)}")
        return jsonify({"status": "failed", "error": str(e)}), 404
    except Exception as e:
        current_app.logger_custom.error(f"/image/seal 处理异常: {str(e)}", exc_info=True)
        return jsonify({"status": "failed", "error": f"处理异常: {str(e)}"}), 500


@image_bp.route('/correct', methods=['POST'])
def document_correct():
    current_app.logger_custom.info("收到 /image/correct 请求")
    try:
        data = request.get_json()
        paths = data['paths']
        current_app.logger_custom.debug(f"文档校正路径列表: {paths}")

        result = image_service.process_doc(paths)
        current_app.logger_custom.info(f"/image/correct 处理完成，返回 {len(result)} 条结果")

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except FileNotFoundError as e:
        current_app.logger_custom.error(f"/image/correct 文件未找到: {str(e)}")
        return jsonify({"status": "failed", "error": str(e)}), 404
    except Exception as e:
        current_app.logger_custom.error(f"/image/correct 处理异常: {str(e)}", exc_info=True)
        return jsonify({"status": "failed", "error": f"处理异常: {str(e)}"}), 500


def configure_output_routes(bp):
    """统一配置所有文件返回路由"""

    # OCR处理结果
    @bp.route('/ocr_outputs/<session_id>/<path:filename>')
    def get_ocr_output(session_id, filename):
        """
        获取OCR处理结果图片（支持多级子文件夹路径）
        """
        base_dir = os.path.join(
            current_app.config['OUTPUT_FOLDER'],
            'ocr',
            session_id
        )
        return send_from_directory(base_dir, filename)

    # 表格识别结果图片（支持 file_0/images/xxx.png）
    @bp.route('/table_outputs/<session_id>/<path:filename>')
    def get_table_output(session_id, filename):
        base_dir = os.path.join(
            current_app.config['OUTPUT_FOLDER'],
            'table',
            session_id
        )
        return send_from_directory(base_dir, filename)

    # 表格数据下载（支持 file_0/data/xxx.xlsx）
    @bp.route('/table_data/<session_id>/<path:filename>')
    def get_table_data(session_id, filename):
        base_dir = os.path.join(
            current_app.config['OUTPUT_FOLDER'],
            'table',
            session_id
        )
        return send_from_directory(
            base_dir,
            filename,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    @bp.route('/seal_outputs/<session_id>/<path:filename>')
    def get_seal_output(session_id, filename):
        data_dir = os.path.join(
            current_app.config['OUTPUT_FOLDER'],
            'seal',
            session_id,
        )
        return send_from_directory(data_dir, filename)

    @bp.route('/correct_outputs/<session_id>/<path:filename>')
    def get_correct_output(session_id, filename):
        data_dir = os.path.join(
            current_app.config['OUTPUT_FOLDER'],
            'doc',
            session_id,
        )
        return send_from_directory(data_dir, filename)


configure_output_routes(image_bp)
