"""课程服务 - 处理课程数据的查询和筛选"""

from patterns.singleton import DataManager


class CourseService:
    """课程相关业务逻辑"""

    @staticmethod
    def get_all_courses(filters=None):
        """
        获取课程列表，支持筛选
        :param filters: 可选筛选条件 { "type": "选修", "keyword": "操作系统" }
        """
        data_mgr = DataManager()
        courses = data_mgr.get_all_courses()

        if not filters:
            return courses

        # 按课程类型筛选
        if filters.get("type"):
            courses = [c for c in courses if c["type"] == filters["type"]]

        # 按关键词搜索（课程名、教师名、课程ID）
        keyword = filters.get("keyword", "").strip()
        if keyword:
            keyword_lower = keyword.lower()
            courses = [
                c for c in courses
                if keyword_lower in c["name"].lower()
                or keyword_lower in c["teacher"].lower()
                or keyword_lower in c["id"].lower()
            ]

        return courses

    @staticmethod
    def get_course_detail(course_id):
        """获取单个课程的详细信息"""
        data_mgr = DataManager()
        return data_mgr.get_course_by_id(course_id)

    @staticmethod
    def get_course_types():
        """获取所有课程类型列表"""
        data_mgr = DataManager()
        types = set(c["type"] for c in data_mgr.get_all_courses())
        return sorted(types)
