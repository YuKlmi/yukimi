"""
命令模式 (Command Pattern)
AI 助手解析用户指令后，将每个操作封装为命令对象。
支持执行 (execute) 和撤销 (undo) 操作。
"""

from abc import ABC, abstractmethod
from datetime import datetime
from .singleton import DataManager
from .strategy import EnrollmentValidator
from .observer import EventManager


class Command(ABC):
    """
    命令接口
    所有具体命令必须实现 execute 和 undo 方法
    """

    @abstractmethod
    def execute(self):
        """执行命令"""
        pass

    @abstractmethod
    def undo(self):
        """撤销命令"""
        pass

    def get_result(self):
        """获取命令执行结果"""
        return self._result if hasattr(self, "_result") else None


class EnrollCommand(Command):
    """具体命令1：选课命令"""

    def __init__(self, student_id, course_id):
        self.student_id = student_id
        self.course_id = course_id
        self._result = None

    def execute(self):
        data_mgr = DataManager()
        student = data_mgr.get_user_by_id(self.student_id)
        course = data_mgr.get_course_by_id(self.course_id)

        if not student:
            self._result = {"success": False, "message": "学生不存在"}
            return self._result
        if not course:
            self._result = {"success": False, "message": "课程不存在"}
            return self._result

        # 获取已选课程（附带课程信息用于校验）
        enrollments = data_mgr.get_enrollments_by_student(self.student_id)
        for e in enrollments:
            e["_course"] = data_mgr.get_course_by_id(e["course_id"])

        # 策略模式：使用校验器执行所有校验策略
        validator = EnrollmentValidator()
        success, message = validator.validate_all(student, course, enrollments)
        if not success:
            self._result = {"success": False, "message": message}
            return self._result

        # 执行选课
        enrollment = {
            "id": len(data_mgr.get_all_enrollments()) + 1,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "enrolled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data_mgr.add_enrollment(enrollment)

        # 更新课程已选人数
        course["enrolled"] = course.get("enrolled", 0) + 1
        data_mgr.save_courses()

        # 观察者模式：触发选课成功事件
        EventManager().emit("enroll_success", {
            "student_id": self.student_id,
            "course_name": course["name"],
            "course_id": self.course_id
        })

        # 检查是否满员
        if course["enrolled"] >= course["capacity"]:
            EventManager().emit("course_full", {
                "course_name": course["name"],
                "course_id": self.course_id
            })

        self._result = {"success": True, "message": f"🎉 选课成功！已成功选择「{course['name']}」"}
        return self._result

    def undo(self):
        """撤销选课 = 退课"""
        data_mgr = DataManager()
        course = data_mgr.get_course_by_id(self.course_id)
        data_mgr.remove_enrollment(self.student_id, self.course_id)
        if course and course["enrolled"] > 0:
            course["enrolled"] -= 1
            data_mgr.save_courses()


class WithdrawCommand(Command):
    """具体命令2：退课命令"""

    def __init__(self, student_id, course_id):
        self.student_id = student_id
        self.course_id = course_id
        self._result = None

    def execute(self):
        data_mgr = DataManager()
        course = data_mgr.get_course_by_id(self.course_id)

        if not course:
            self._result = {"success": False, "message": "课程不存在"}
            return self._result

        # 检查是否已选该课
        enrollment = data_mgr.get_enrollment(self.student_id, self.course_id)
        if not enrollment:
            self._result = {"success": False, "message": f"你还没有选择课程「{course['name']}」"}
            return self._result

        # 执行退课
        data_mgr.remove_enrollment(self.student_id, self.course_id)

        # 更新课程已选人数
        if course["enrolled"] > 0:
            course["enrolled"] -= 1
            data_mgr.save_courses()

        # 观察者模式：触发退课成功事件
        EventManager().emit("withdraw_success", {
            "student_id": self.student_id,
            "course_name": course["name"],
            "course_id": self.course_id
        })

        self._result = {"success": True, "message": f"✅ 退课成功！已成功退选「{course['name']}」"}
        return self._result

    def undo(self):
        pass  # 退课的撤销，这里简单定义为重新选回


class QueryScheduleCommand(Command):
    """具体命令3：查询课表命令"""

    def __init__(self, student_id, day=None):
        self.student_id = student_id
        self.day = day
        self._result = None

    def execute(self):
        data_mgr = DataManager()
        enrollments = data_mgr.get_enrollments_by_student(self.student_id)

        schedule_items = []
        for enroll in enrollments:
            course = data_mgr.get_course_by_id(enroll["course_id"])
            if course:
                for slot in course.get("schedule", []):
                    if self.day and slot["day"] != self.day:
                        continue
                    schedule_items.append({
                        "course_name": course["name"],
                        "teacher": course["teacher"],
                        "day": slot["day"],
                        "start": slot["start"],
                        "end": slot["end"],
                        "location": slot["location"],
                    })

        # 按星期和时间排序
        day_order = {"周一": 1, "周二": 2, "周三": 3, "周四": 4, "周五": 5, "周六": 6, "周日": 7}
        schedule_items.sort(key=lambda x: (day_order.get(x["day"], 99), x["start"]))

        # 将课表数据格式化为可读文本
        if not schedule_items:
            if self.day:
                msg = f"{self.day}没有安排课程"
            else:
                msg = "你目前还没有选择任何课程"
            self._result = {"success": True, "data": [], "message": msg}
            return self._result

        period_names = {1: "第1-2节", 3: "第3-4节", 5: "第5-6节", 7: "第7-8节", 9: "第9-10节"}
        def period_str(start, end):
            label = period_names.get(start, f"第{start}-{end}节")
            return f"{label}（{start}-{end}节）"

        if self.day:
            lines = [f"📚 {self.day}课表："]
        else:
            lines = ["📚 本周课表："]
        current_day = None
        for item in schedule_items:
            if item["day"] != current_day:
                current_day = item["day"]
                lines.append(f"\n【{current_day}】")
            lines.append(
                f"  📖 {item['course_name']}（{item['teacher']}）\n"
                f"     {period_str(item['start'], item['end'])} @ {item['location']}"
            )

        self._result = {
            "success": True,
            "data": schedule_items,
            "message": "\n".join(lines)
        }
        return self._result

    def undo(self):
        pass


class RecommendCommand(Command):
    """具体命令4：推荐课程命令"""

    def __init__(self, student_id, course_type=None):
        self.student_id = student_id
        self.course_type = course_type
        self._result = None

    def execute(self):
        data_mgr = DataManager()
        enrollments = data_mgr.get_enrollments_by_student(self.student_id)
        enrolled_ids = {e["course_id"] for e in enrollments}

        # 找出未选且有余量的课程
        candidates = []
        for course in data_mgr.get_all_courses():
            if course["id"] in enrolled_ids:
                continue
            if course["enrolled"] >= course["capacity"]:
                continue
            if self.course_type and course["type"] != self.course_type:
                continue
            candidates.append(course)

        if not candidates:
            self._result = {"success": True, "data": None, "message": "没有找到适合推荐的课程"}
            return self._result

        # 按余量比例排序，推荐最不紧张但还有空位的课
        candidates.sort(key=lambda c: c["enrolled"] / c["capacity"] if c["capacity"] > 0 else 1)
        recommended = candidates[:3]

        lines = [f"💡 推荐以下课程（共{len(recommended)}门）："]
        for i, c in enumerate(recommended, 1):
            remaining = c["capacity"] - c["enrolled"]
            credit_type = "必修" if c.get("required") else "选修"
            lines.append(
                f"\n{i}. {c['name']}（{credit_type}，{c['credits']}学分）\n"
                f"   授课教师：{c['teacher']}\n"
                f"   余量：{remaining}/{c['capacity']}人\n"
                f"   时间：{c.get('schedule', [{}])[0].get('day', '待定')} "
                f"{c.get('schedule', [{}])[0].get('start', '')}-"
                f"{c.get('schedule', [{}])[0].get('end', '')}节 @ "
                f"{c.get('schedule', [{}])[0].get('location', '待定')}"
            )

        self._result = {
            "success": True,
            "data": recommended,
            "message": "\n".join(lines)
        }
        return self._result

    def undo(self):
        pass


class QueryCourseCommand(Command):
    """具体命令5：查询课程信息命令"""

    def __init__(self, keyword):
        self.keyword = keyword
        self._result = None

    def execute(self):
        data_mgr = DataManager()
        keyword = self.keyword.lower()

        results = []
        for course in data_mgr.get_all_courses():
            if (keyword in course["name"].lower()
                    or keyword in course["teacher"].lower()
                    or keyword in course["id"].lower()):
                results.append(course)

        if not results:
            self._result = {"success": True, "data": None, "message": f"没有找到与「{self.keyword}」相关的课程"}
            return self._result

        lines = [f"🔍 找到 {len(results)} 门与「{self.keyword}」相关的课程："]
        for i, c in enumerate(results, 1):
            credit_type = "必修" if c.get("required") else "选修"
            lines.append(
                f"\n{i}. {c['name']}（{credit_type}，{c['credits']}学分）\n"
                f"   授课教师：{c['teacher']}\n"
                f"   上课时间：{c.get('schedule', [{}])[0].get('day', '待定')} "
                f"{c.get('schedule', [{}])[0].get('start', '')}-"
                f"{c.get('schedule', [{}])[0].get('end', '')}节\n"
                f"   上课地点：{c.get('schedule', [{}])[0].get('location', '待定')}"
            )

        self._result = {"success": True, "data": results, "message": "\n".join(lines)}
        return self._result

    def undo(self):
        pass


class CommandInvoker:
    """
    命令调度器 (Invoker)
    接收 AI 解析结果，根据 intent 创建并执行对应的命令
    """

    def __init__(self):
        self._history = []  # 命令执行历史，支持撤销

    def execute(self, command):
        """执行命令并记录到历史"""
        result = command.execute()
        self._history.append(command)
        return result

    def undo_last(self):
        """撤销最后一条命令"""
        if self._history:
            command = self._history.pop()
            command.undo()
            return True
        return False

    def parse_and_execute(self, student_id, intent_data):
        """
        解析 AI 返回的结构化数据并执行
        :param student_id: 当前学生ID
        :param intent_data: AI 解析结果 {"intent": "...", "course": "...", ...}
        """
        intent = intent_data.get("intent", "chat")
        data_mgr = DataManager()

        if intent == "enroll":
            course_name = intent_data.get("course", "")
            course = self._find_course_by_name(course_name, data_mgr)
            if not course:
                return {"success": False, "message": f"未找到课程「{course_name}」"}
            command = EnrollCommand(student_id, course["id"])
            return self.execute(command)

        elif intent == "withdraw":
            course_name = intent_data.get("course", "")
            course = self._find_course_by_name(course_name, data_mgr)
            if not course:
                return {"success": False, "message": f"未找到课程「{course_name}」"}
            command = WithdrawCommand(student_id, course["id"])
            return self.execute(command)

        elif intent == "query_schedule":
            day = intent_data.get("day", None)
            command = QueryScheduleCommand(student_id, day)
            return self.execute(command)

        elif intent == "recommend":
            course_type = intent_data.get("course_type", None)
            command = RecommendCommand(student_id, course_type)
            return self.execute(command)

        elif intent == "query_course":
            keyword = intent_data.get("course", intent_data.get("keyword", ""))
            command = QueryCourseCommand(keyword)
            return self.execute(command)

        elif intent == "chat":
            return {"success": True, "is_chat": True, "message": intent_data.get("message", "")}

        return {"success": False, "message": "无法识别的指令"}

    def _find_course_by_name(self, name, data_mgr):
        """根据课程名称（支持模糊匹配）查找课程"""
        courses = data_mgr.get_all_courses()
        # 先精确匹配
        for course in courses:
            if course["name"] == name:
                return course
        # 模糊匹配
        for course in courses:
            if name in course["name"]:
                return course
        return None
