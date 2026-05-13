"""
单例模式 (Singleton Pattern)
确保 DataManager 在整个应用中只有一个实例，
所有模块通过统一的数据入口访问和修改数据。
"""

import json
import os


class DataManager:
    """
    全局数据管理器 - 单例模式
    负责所有 JSON 数据的加载、保存和访问
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        # 控制实例化：如果实例不存在则创建，否则返回已有实例
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, data_dir=None):
        # 确保初始化只执行一次
        if self._initialized:
            return

        self.data_dir = data_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        self.courses_file = os.path.join(self.data_dir, "courses.json")
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.enrollments_file = os.path.join(self.data_dir, "enrollments.json")

        self._courses = []
        self._users = []
        self._enrollments = []

        self._load_all()
        DataManager._initialized = True

    def _load_all(self):
        """加载所有 JSON 数据文件"""
        self._courses = self._load_json(self.courses_file)
        self._users = self._load_json(self.users_file)
        self._enrollments = self._load_json(self.enrollments_file)

    def _load_json(self, filepath):
        """从 JSON 文件读取数据"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_json(self, filepath, data):
        """将数据写入 JSON 文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ---- 课程相关 ----
    def get_all_courses(self):
        return self._courses

    def get_course_by_id(self, course_id):
        for course in self._courses:
            if course["id"] == course_id:
                return course
        return None

    def save_courses(self):
        self._save_json(self.courses_file, self._courses)

    # ---- 用户相关 ----
    def get_all_users(self):
        return self._users

    def get_user_by_id(self, user_id):
        for user in self._users:
            if user["id"] == user_id:
                return user
        return None

    def get_user_by_username(self, username):
        for user in self._users:
            if user["username"] == username:
                return user
        return None

    def save_users(self):
        self._save_json(self.users_file, self._users)

    # ---- 选课记录相关 ----
    def get_all_enrollments(self):
        return self._enrollments

    def get_enrollments_by_student(self, student_id):
        return [e for e in self._enrollments if e["student_id"] == student_id]

    def get_enrollment(self, student_id, course_id):
        for e in self._enrollments:
            if e["student_id"] == student_id and e["course_id"] == course_id:
                return e
        return None

    def add_enrollment(self, enrollment):
        self._enrollments.append(enrollment)
        self.save_enrollments()

    def remove_enrollment(self, student_id, course_id):
        self._enrollments = [
            e for e in self._enrollments
            if not (e["student_id"] == student_id and e["course_id"] == course_id)
        ]
        self.save_enrollments()

    def save_enrollments(self):
        self._save_json(self.enrollments_file, self._enrollments)

    # ---- 重置数据（调试用） ----
    def reload(self):
        self._load_all()
