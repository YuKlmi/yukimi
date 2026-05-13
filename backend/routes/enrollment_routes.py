"""选课/退课/课表相关 API 路由"""

from flask import Blueprint, request, jsonify
from services.enrollment_service import EnrollmentService

enrollment_bp = Blueprint("enrollment", __name__, url_prefix="/api/enrollments")


@enrollment_bp.route("", methods=["POST"])
def enroll():
    """选课接口"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "请提供选课信息"}), 400

    student_id = data.get("student_id")
    course_id = data.get("course_id")

    if not student_id or not course_id:
        return jsonify({"success": False, "message": "学生ID和课程ID不能为空"}), 400

    service = EnrollmentService()
    result = service.enroll(student_id, course_id)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@enrollment_bp.route("/<course_id>", methods=["DELETE"])
def withdraw(course_id):
    """退课接口"""
    student_id = request.args.get("student_id")
    if not student_id:
        return jsonify({"success": False, "message": "缺少学生ID"}), 400

    service = EnrollmentService()
    result = service.withdraw(student_id, course_id)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@enrollment_bp.route("", methods=["GET"])
def get_my_courses():
    """获取学生已选课程列表"""
    student_id = request.args.get("student_id")
    if not student_id:
        return jsonify({"success": False, "message": "缺少学生ID"}), 400

    courses = EnrollmentService.get_my_courses(student_id)
    return jsonify({"success": True, "data": courses})


@enrollment_bp.route("/schedule", methods=["GET"])
def get_schedule():
    """获取学生课表"""
    student_id = request.args.get("student_id")
    if not student_id:
        return jsonify({"success": False, "message": "缺少学生ID"}), 400

    schedule = EnrollmentService.get_schedule(student_id)
    return jsonify({"success": True, "data": schedule})
