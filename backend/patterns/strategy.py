"""
策略模式 (Strategy Pattern)
选课校验策略族：每种校验规则是一个独立的策略，
可自由组合，新增规则无需修改核心选课逻辑。
"""

from abc import ABC, abstractmethod


class EnrollmentStrategy(ABC):
    """
    策略接口：所有选课校验策略的基类
    """
    @abstractmethod
    def validate(self, student, course, enrollments):
        """
        执行校验
        :param student: 学生信息
        :param course: 待选课程
        :param enrollments: 该学生已有的选课记录列表
        :return: (True, None) 或 (False, 错误消息)
        """
        pass


class TimeConflictStrategy(EnrollmentStrategy):
    """策略1：检查课程时间是否与已选课程冲突"""

    def validate(self, student, course, enrollments):
        # 获取待选课程的所有上课时间段
        new_schedule = course.get("schedule", [])

        # 遍历已选课程的排课，检查是否有时间重叠
        for enrollment in enrollments:
            enrolled_course = enrollment.get("_course")
            if not enrolled_course:
                continue
            for exist_slot in enrolled_course.get("schedule", []):
                for new_slot in new_schedule:
                    if self._is_conflict(exist_slot, new_slot):
                        return (False,
                                f"时间冲突：课程「{course['name']}」与已选课程「{enrolled_course['name']}」"
                                f"在{new_slot['day']}第{new_slot['start']}-{new_slot['end']}节冲突")
        return (True, None)

    def _is_conflict(self, slot_a, slot_b):
        """判断两个时间段是否有重叠"""
        if slot_a["day"] != slot_b["day"]:
            return False
        # 判断时间段是否有交集：[a_start, a_end] 与 [b_start, b_end]
        return not (slot_a["end"] < slot_b["start"] or slot_a["start"] > slot_b["end"])


class CreditLimitStrategy(EnrollmentStrategy):
    """策略2：检查选课后总学分是否超过上限"""

    def validate(self, student, course, enrollments):
        max_credits = student.get("max_credits", 25)
        # 计算已选课程总学分
        current_credits = sum(e.get("_course", {}).get("credits", 0) for e in enrollments)
        if current_credits + course["credits"] > max_credits:
            return (False,
                    f"学分超限：当前已选{current_credits}学分，课程「{course['name']}」{course['credits']}学分，"
                    f"上限{max_credits}学分")
        return (True, None)


class CapacityStrategy(EnrollmentStrategy):
    """策略3：检查课程是否已满员"""

    def validate(self, student, course, enrollments):
        if course["enrolled"] >= course["capacity"]:
            return (False, f"课程已满：{course['name']} 容量{course['capacity']}人，已满员")
        return (True, None)


class DuplicateStrategy(EnrollmentStrategy):
    """策略4：检查是否已经选过该课程"""

    def validate(self, student, course, enrollments):
        for enrollment in enrollments:
            if enrollment["course_id"] == course["id"]:
                return (False, f"重复选课：已经选过课程「{course['name']}」了")
        return (True, None)


class EnrollmentValidator:
    """
    校验器上下文 (Context)
    持有策略列表，按顺序执行所有策略
    """

    def __init__(self):
        # 注册默认策略集，可按需增删
        self._strategies = [
            DuplicateStrategy(),
            CapacityStrategy(),
            CreditLimitStrategy(),
            TimeConflictStrategy(),
        ]

    def add_strategy(self, strategy):
        """动态添加策略"""
        self._strategies.append(strategy)

    def remove_strategy(self, strategy_class):
        """按类型移除策略"""
        self._strategies = [s for s in self._strategies if not isinstance(s, strategy_class)]

    def validate_all(self, student, course, enrollments):
        """
        执行所有校验策略
        :return: (True, None) 或 (False, 第一条失败的消息)
        """
        errors = []
        for strategy in self._strategies:
            success, message = strategy.validate(student, course, enrollments)
            if not success:
                errors.append(message)
        if errors:
            return (False, errors[0])
        return (True, None)
