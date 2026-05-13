"""
Flask 应用主入口 - 选课系统后端
启动前请先配置 .env 文件中的 DEEPSEEK_API_KEY
"""

import sys
import os

# 将 backend 目录加入 Python 路径，确保直接运行 python app.py 时能正确导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from config import Config
from patterns.singleton import DataManager
from patterns.observer import EventManager, LoggerObserver, NotificationObserver


def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["DEBUG"] = Config.DEBUG

    # 允许跨域访问（前端开发时需访问不同端口）
    CORS(app, supports_credentials=True)

    # 初始化单例模式 - 全局数据管理器
    # 首次访问 DataManager() 时会加载所有 JSON 数据
    DataManager(Config.DATA_DIR)

    # 初始化观察者模式 - 注册全局观察者
    event_mgr = EventManager()
    event_mgr.register(LoggerObserver())            # 观察者1: 日志记录
    event_mgr.register(NotificationObserver())      # 观察者2: 通知提醒

    # 注册蓝图（API 路由）
    from routes.auth_routes import auth_bp
    from routes.course_routes import course_bp
    from routes.enrollment_routes import enrollment_bp
    from routes.ai_routes import ai_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(enrollment_bp)
    app.register_blueprint(ai_bp)

    return app


# 启动应用
if __name__ == "__main__":
    app = create_app()
    print(f"选课系统后端启动成功，访问地址: http://localhost:{Config.PORT}")
    print(f"AI 助手模式: {'DeepSeek API（已配置）' if Config.DEEPSEEK_API_KEY else '本地规则匹配（降级模式）'}")
    app.run(host="0.0.0.0", port=Config.PORT)
