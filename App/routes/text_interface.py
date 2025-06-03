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
        api_key = data.get('apiKey')
        base_url = data.get('baseUrl')
        text_service.ensure_key(api_key, base_url)  # 设置首次使用的 key

        results = text_service.compare_documents(paths)
        return jsonify({"status": "success", "data": results}), 200
    except Exception as e:
        current_app.logger_custom.error(f"/text/compare 处理失败: {str(e)}", exc_info=True)
        return jsonify({"status": "failed", "error": f"处理异常: {str(e)}"}), 500


@text_bp.route('/extract', methods=['POST'])
def texts_extract():
    current_app.logger_custom.info("收到 /text/extract 请求")
    try:
        data = request.get_json()
        paths = data['paths']
        api_key = data.get('apiKey')
        base_url = data.get('baseUrl')
        text_service.ensure_key(api_key, base_url)  # 🔐 设置首次使用的 key

        results = text_service.extract_contract_info(paths)
        return jsonify({"status": "success", "data": results}), 200
    except Exception as e:
        current_app.logger_custom.error(f"/text/extract 处理失败: {str(e)}", exc_info=True)
        return jsonify({"status": "failed", "error": f"处理异常: {str(e)}"}), 500
