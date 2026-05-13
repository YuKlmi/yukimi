"""AI 助手 API 路由"""

from flask import Blueprint, request, jsonify
from services.ai_service import AIService

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")

# AI 服务实例（单次对话不保存状态）
_ai_service = AIService()


@ai_bp.route("/chat", methods=["POST"])
def chat():
    """AI 对话接口"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "请输入消息"}), 400

    student_id = data.get("student_id")
    message = data.get("message", "").strip()

    if not student_id:
        return jsonify({"success": False, "message": "缺少学生ID"}), 400

    if not message:
        return jsonify({"success": False, "message": "消息不能为空"}), 400

    # 交给 AI 服务处理
    result = _ai_service.handle_message(student_id, message)
    return jsonify(result)
