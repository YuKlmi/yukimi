"""认证服务 - 处理登录和用户身份验证"""

from patterns.singleton import DataManager


class AuthService:
    """用户认证逻辑"""

    @staticmethod
    def login(username, password):
        """
        验证用户名和密码
        :return: (成功?, 消息, 用户数据或None)
        """
        data_mgr = DataManager()
        user = data_mgr.get_user_by_username(username)

        if not user:
            return (False, "用户名不存在", None)

        if user["password"] != password:
            return (False, "密码错误", None)

        # 返回用户信息（不含密码）
        user_info = {
            "id": user["id"],
            "username": user["username"],
            "name": user["name"],
            "max_credits": user["max_credits"]
        }
        return (True, "登录成功", user_info)

    @staticmethod
    def change_password(username, old_password, new_password):
        """
        修改用户密码
        :return: (成功?, 消息)
        """
        if not new_password or len(new_password) < 4:
            return (False, "新密码长度不能少于4位")

        data_mgr = DataManager()
        user = data_mgr.get_user_by_username(username)

        if not user:
            return (False, "用户不存在")

        if user["password"] != old_password:
            return (False, "原密码错误")

        user["password"] = new_password
        data_mgr.save_users()
        return (True, "密码修改成功")
