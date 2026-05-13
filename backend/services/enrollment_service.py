"""选课服务 - 处理选课、退课、课表查询等业务"""

from patterns.singleton import DataManager
from patterns.command import EnrollCommand, WithdrawCommand, CommandInvoker


class EnrollmentService:
    """选课退课相关业务"""

    def __init__(self):
        self._invoker = CommandInvoker()

    def enroll(self, student_id, course_id):
        """选课：通过命令模式执行"""
        command = EnrollCommand(student_id, course_id)
        return self._invoker.execute(command)

    def withdraw(self, student_id, course_id):
        """退课：通过命令模式执行"""
        command = WithdrawCommand(student_id, course_id)
        return self._invoker.execute(command)

    @staticmethod
    def get_my_courses(student_id):
        """
        获取学生已选课程列表（附带课程详细信息）
        """
        data_mgr = DataManager()
        enrollments = data_mgr.get_enrollments_by_student(student_id)

        results = []
        for e in enrollments:
            course = data_mgr.get_course_by_id(e["course_id"])
            if course:
                results.append({
                    **e,
                    "_course": course
                })

        return results

    @staticmethod
    def get_schedule(student_id):
        """
        获取学生课表（所有已选课程按时间段排列）
        """
        data_mgr = DataManager()
        enrollments = data_mgr.get_enrollments_by_student(student_id)

        day_order = {"周一": 1, "周二": 2, "周三": 3, "周四": 4, "周五": 5}
        schedule_grid = {}

        for e in enrollments:
            course = data_mgr.get_course_by_id(e["course_id"])
            if not course:
                continue
            for slot in course.get("schedule", []):
                day = slot["day"]
                if day not in schedule_grid:
                    schedule_grid[day] = []
                schedule_grid[day].append({
                    "course_name": course["name"],
                    "teacher": course["teacher"],
                    "location": slot["location"],
                    "start": slot["start"],
                    "end": slot["end"],
                    "day": day,
                })

        # 排序
        for day in schedule_grid:
            schedule_grid[day].sort(key=lambda x: x["start"])

        return schedule_grid
