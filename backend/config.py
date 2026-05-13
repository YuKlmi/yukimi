import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()


class Config:
    # Flask 相关
    SECRET_KEY = os.getenv("SECRET_KEY", "course-system-secret-key-2026")
    DEBUG = True

    # 服务器端口
    PORT = int(os.getenv("PORT", 5000))

    # DeepSeek API 配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
    DEEPSEEK_MODEL = "deepseek-chat"

    # JSON 数据文件路径
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    COURSES_FILE = os.path.join(DATA_DIR, "courses.json")
    USERS_FILE = os.path.join(DATA_DIR, "users.json")
    ENROLLMENTS_FILE = os.path.join(DATA_DIR, "enrollments.json")

    # 选课限制
    MAX_CREDITS_PER_STUDENT = 25
