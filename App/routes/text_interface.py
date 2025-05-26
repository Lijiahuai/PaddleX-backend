from flask import Blueprint, request, jsonify, current_app
from App.services.text_service import TextService

text_bp = Blueprint('text', __name__, url_prefix='/text')
text_service = TextService()


@text_bp.route('/compare', methods=['POST'])
def texts_compare():
    current_app.logger_custom.info("收到 /text/compare 请求")
    try:
        data = request.get_json()
        paths = data['paths']
        current_app.logger_custom.debug(f"文本比较路径列表: {paths}")

        results = text_service.compare_documents(paths)
        current_app.logger_custom.info(f"/text/compare 处理完成，返回 {len(results)} 条结果")

        return jsonify({
            "status": "success",
            "data": results
        }), 200

    except Exception as e:
        current_app.logger_custom.error(f"/text/compare 处理失败: {str(e)}", exc_info=True)
        return jsonify({
            "status": "failed",
            "error": f"处理异常: {str(e)}"
        }), 500


@text_bp.route('/extract', methods=['POST'])
def texts_extract():
    current_app.logger_custom.info("收到 /text/extract 请求")
    try:
        data = request.get_json()
        paths = data['paths']
        current_app.logger_custom.debug(f"文本提取文件ID列表: {paths}")

        results = text_service.extract_contract_info(paths)
        current_app.logger_custom.info(f"/text/extract 处理完成，返回 {len(results)} 条结果")

        return jsonify({
            "status": "success",
            "data": results
        }), 200

    except Exception as e:
        current_app.logger_custom.error(f"/text/extract 处理失败: {str(e)}", exc_info=True)
        return jsonify({
            "status": "failed",
            "error": f"处理异常: {str(e)}"
        }), 500
