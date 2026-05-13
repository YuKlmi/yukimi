"""课程相关 API 路由"""

from flask import Blueprint, request, jsonify
from services.course_service import CourseService

course_bp = Blueprint("course", __name__, url_prefix="/api/courses")


@course_bp.route("", methods=["GET"])
def get_courses():
    """获取课程列表（支持筛选和搜索）"""
    filters = {}
    if request.args.get("type"):
        filters["type"] = request.args["type"]
    if request.args.get("keyword"):
        filters["keyword"] = request.args["keyword"]

    courses = CourseService.get_all_courses(filters or None)
    return jsonify({"success": True, "data": courses})


@course_bp.route("/types", methods=["GET"])
def get_course_types():
    """获取课程类型列表"""
    types = CourseService.get_course_types()
    return jsonify({"success": True, "data": types})


@course_bp.route("/<course_id>", methods=["GET"])
def get_course_detail(course_id):
    """获取课程详情"""
    course = CourseService.get_course_detail(course_id)
    if not course:
        return jsonify({"success": False, "message": "课程不存在"}), 404
    return jsonify({"success": True, "data": course})
