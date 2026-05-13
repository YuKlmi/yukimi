"""
观察者模式 (Observer Pattern)
事件管理：当选课/退课等事件发生时，通知所有注册的观察者。
例如：选课成功后自动刷新课程列表的已选人数。
"""

from abc import ABC, abstractmethod


class EventObserver(ABC):
    """
    观察者接口
    所有需要接收事件通知的模块实现此接口
    """

    @abstractmethod
    def on_event(self, event_type, data):
        """
        事件回调方法
        :param event_type: 事件类型字符串
        :param data: 事件相关数据
        """
        pass


class EventManager:
    """
    事件管理器 - 主题 (Subject)
    维护观察者列表，提供注册、注销和通知功能
    整个应用共享一个实例
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._observers = []
        return cls._instance

    def register(self, observer):
        """注册观察者"""
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer):
        """注销观察者"""
        if observer in self._observers:
            self._observers.remove(observer)

    def emit(self, event_type, data=None):
        """
        触发事件，通知所有观察者
        :param event_type: 事件类型
            - "enroll_success": 选课成功
            - "withdraw_success": 退课成功
            - "course_full": 课程满员
        :param data: 事件数据字典
        """
        for observer in self._observers:
            observer.on_event(event_type, data)


class LoggerObserver(EventObserver):
    """观察者1：日志记录 - 记录所有事件到日志"""

    def on_event(self, event_type, data):
        log_map = {
            "enroll_success": f"[选课成功] 学生{data.get('student_id')} 选了 {data.get('course_name')}",
            "withdraw_success": f"[退课成功] 学生{data.get('student_id')} 退了 {data.get('course_name')}",
            "course_full": f"[课程满员] {data.get('course_name')} 已满",
        }
        message = log_map.get(event_type, f"[事件] {event_type}: {data}")
        print(message)


class NotificationObserver(EventObserver):
    """观察者2：通知提醒 - 生成用户可读的通知消息（可被前端拉取）"""

    def __init__(self):
        self._notifications = []

    def on_event(self, event_type, data):
        notification_map = {
            "enroll_success": f"🎉 选课成功！已成功选择「{data.get('course_name')}」",
            "withdraw_success": f"✅ 退课成功！已成功退选「{data.get('course_name')}」",
            "course_full": f"⚠️ 课程「{data.get('course_name')}」已满员",
        }
        message = notification_map.get(event_type, f"系统消息: {event_type}")
        self._notifications.append({
            "type": event_type,
            "message": message,
            "data": data
        })

    def get_notifications(self):
        """获取所有通知并清空"""
        notifications = list(self._notifications)
        self._notifications.clear()
        return notifications
