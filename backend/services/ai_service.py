"""
AI 服务 - 对接 DeepSeek API
将用户自然语言解析为结构化意图数据，然后交由命令模式执行
"""

import json
import re
import requests
from config import Config
from patterns.command import CommandInvoker


# 系统提示词：告诉 DeepSeek 如何理解选课相关的自然语言
SYSTEM_PROMPT = """你是一个选课系统的AI助手。你需要理解用户的自然语言指令，并返回结构化的JSON数据。

支持的意图列表(严格使用以下intent值):
- enroll: 选课，如"选操作系统课"、"帮我选高数"
- withdraw: 退课，如"退掉高数"、"把英语课退了"
- query_schedule: 查询课表，如"我周一有什么课"、"今天上什么课"
- recommend: 推荐课程，如"推荐一门选修课"、"有什么好的课推荐"
- query_course: 课程信息查询，如"操作系统几点上课"、"数据结构在哪上"
- chat: 普通对话，如"你好"、"谢谢"、"你是谁"

返回格式要求(务必只返回纯JSON，不要包含其他文字):
1. 选课: {"intent": "enroll", "course": "课程名称"}
2. 退课: {"intent": "withdraw", "course": "课程名称"}
3. 查课表: {"intent": "query_schedule", "day": "周一"} (day可为空查全部)
4. 推荐: {"intent": "recommend", "course_type": "选修"} (course_type可为空)
5. 查课程: {"intent": "query_course", "course": "关键词"}
6. 普通对话: {"intent": "chat", "message": "你的回复内容"}

注意：课程名称请使用中文标准名称，如"操作系统"、"数据结构"等。"""


class AIService:
    """AI 服务：解析用户输入并执行业务操作"""

    def __init__(self):
        self._invoker = CommandInvoker()

    def handle_message(self, student_id, user_message):
        """
        处理用户消息的主入口
        1. 优先调用 DeepSeek API 解析意图
        2. API失败则使用本地关键词匹配降级
        3. 将解析结果交给命令模式执行
        """
        # 第一步：调用 DeepSeek 解析意图
        intent_data = self._call_deepseek(user_message)

        if not intent_data:
            # 降级方案：本地关键词匹配
            intent_data = self._local_fallback(user_message)

        # 第二步：如果是普通对话，直接返回消息
        if intent_data.get("intent") == "chat":
            return {
                "success": True,
                "is_chat": True,
                "message": intent_data.get("message", "你好！我是选课助手，可以帮你选课、退课、查课表等。")
            }

        # 第三步：通过命令模式执行业务操作
        return self._invoker.parse_and_execute(student_id, intent_data)

    def _call_deepseek(self, message):
        """调用 DeepSeek API 进行意图识别"""
        api_key = Config.DEEPSEEK_API_KEY
        if not api_key:
            return None

        try:
            response = requests.post(
                Config.DEEPSEEK_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "model": Config.DEEPSEEK_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": message}
                    ],
                    "temperature": 0.1,  # 低温度，保持输出稳定
                    "max_tokens": 200,
                },
                timeout=10
            )

            if response.status_code != 200:
                print(f"DeepSeek API 错误: {response.status_code} - {response.text}")
                return None

            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()

            # 提取 JSON（防止模型返回额外文字）
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(content)

        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            print(f"DeepSeek API 调用失败: {e}")
            return None

    def _local_fallback(self, message):
        """
        本地关键词匹配降级方案
        当 DeepSeek API 不可用时使用
        """
        msg = message.strip()

        # 问候
        if any(kw in msg for kw in ["你好", "hello", "hi", "在吗", "你是谁"]):
            return {
                "intent": "chat",
                "message": "你好！我是你的选课助手，可以帮你选课、退课、查课表、推荐课程。试试对我说「选操作系统课」或「推荐一门选修课」吧！"
            }

        # 选课意图
        enroll_match = re.search(r'(选|加|报|选择|报名|注册)\s*(.*?)(课|课程| class)?$', msg)
        if enroll_match:
            course_name = enroll_match.group(2).strip()
            if course_name:
                return {"intent": "enroll", "course": course_name}

        # 退课意图
        withdraw_match = re.search(r'(退|取消|删|移除|drop)\s*(.*?)(课|课程)?$', msg)
        if withdraw_match:
            course_name = withdraw_match.group(2).strip()
            if course_name:
                return {"intent": "withdraw", "course": course_name}

        # 查课表
        if "课表" in msg or "课程表" in msg or "上什么课" in msg or "有什么课" in msg:
            day = None
            for d in ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]:
                if d in msg:
                    day = d
                    break
            return {"intent": "query_schedule", "day": day}

        # 推荐课程
        if "推荐" in msg or "建议" in msg:
            course_type = None
            for t in ["必修", "选修", "通识"]:
                if t in msg:
                    course_type = t
                    break
            return {"intent": "recommend", "course_type": course_type}

        # 查询课程信息
        query_match = re.search(r'(查询|查|搜索|找|查看|看看)\s*(.*?)(课|课程|信息)?$', msg)
        if query_match:
            keyword = query_match.group(2).strip()
            if keyword:
                return {"intent": "query_course", "course": keyword}

        # 如果只提到课程名，默认理解为查询
        course_keywords = ["操作系统", "数据结构", "网络", "高数", "英语", "数据库", "设计模式"]
        for kw in course_keywords:
            if kw in msg:
                return {"intent": "query_course", "course": kw}

        return {
            "intent": "chat",
            "message": "我没理解你的意思。你可以这样跟我说话：\n- 「选操作系统课」\n- 「退掉高数」\n- 「我周一有什么课」\n- 「推荐一门选修课」"
        }
