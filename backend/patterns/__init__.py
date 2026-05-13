# 设计模式包 - 集中管理和导出所有设计模式
from .singleton import DataManager
from .strategy import (
    EnrollmentStrategy,
    TimeConflictStrategy,
    CreditLimitStrategy,
    CapacityStrategy,
    DuplicateStrategy,
    EnrollmentValidator,
)
from .observer import EventManager, EventObserver
from .command import Command, CommandInvoker, EnrollCommand, WithdrawCommand, QueryScheduleCommand, RecommendCommand, QueryCourseCommand
