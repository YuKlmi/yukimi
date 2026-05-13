"""认证相关 API 路由"""

from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """用户登录接口"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "请提供登录信息"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "用户名和密码不能为空"}), 400

    success, message, user_info = AuthService.login(username, password)
    if success:
        return jsonify({"success": True, "message": message, "data": user_info})
    else:
        return jsonify({"success": False, "message": message}), 401


@auth_bp.route("/change-password", methods=["POST"])
def change_password():
    """修改密码接口"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "请提供必要信息"}), 400

    username = data.get("username", "").strip()
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not username or not old_password or not new_password:
        return jsonify({"success": False, "message": "参数不完整"}), 400

    success, message = AuthService.change_password(username, old_password, new_password)
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "message": message}), 400
