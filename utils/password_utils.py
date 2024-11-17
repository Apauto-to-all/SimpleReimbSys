import os
import jwt  # 导入jwt模块
from datetime import datetime, timedelta, timezone
import bcrypt
import json

import config  # 导入config模块


# 加密密码
async def encrypt_password(password: str) -> str:
    """
    :param password: 密码
    :return: 返回加密后的密码
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()  # 返回加密后的密码，长度为60位


# 验证密码
async def verify_password(hashed_password: str, password: str) -> bool:
    """
    :param hashed_password: 加密后的密码
    :param password: 密码
    :return: 返回密码是否正确，True表示密码正确，False表示密码错误
    """
    try:
        return bcrypt.checkpw(
            password.encode(), hashed_password.encode()
        )  # 返回True或False，表示密码是否正确
    except Exception as e:
        return False  # 返回False，表示密码错误


ALGORITHM = "HS256"  # 加密算法


# 生成JWT
async def get_access_jwt(user: str) -> str:
    """
    生成JWT
    :param user: 用户信息
    :return: JWT Token
    """
    import secrets

    SECRET_KEY = "SECRET_KEY"
    login_time_minute = 36000  # 登入时间分钟
    if os.path.exists(config.private_info_json):
        with open(config.private_info_json, "r") as f:
            private_info = json.load(f)
            SECRET_KEY = private_info.get("SECRET_KEY")
            login_time_minute = private_info.get("login_time_minute")

    payload = {
        "jti": secrets.token_hex(16),  # JWT ID
        "user": user,
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=login_time_minute),  # 使用带有UTC时区信息的datetime对象
    }
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)  # 生成token
    return access_token


# 验证JWT
async def get_user_from_jwt(token: str) -> str:
    """
    验证JWT，返回用户名，如果Token无效，返回空字符串
    :param token: JWT Token
    :return: 用户信息，如果Token无效，返回None
    """
    try:
        SECRET_KEY = "SECRET_KEY"
        if os.path.exists(config.private_info_json):
            with open(config.private_info_json, "r") as f:
                private_info = json.load(f)
                SECRET_KEY = private_info.get("SECRET_KEY")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # 解码token
        return payload.get("user")  # 返回用户信息
    except jwt.ExpiredSignatureError:
        "Token已过期"
        return None
    except jwt.InvalidTokenError:
        "无效的Token"
        return None
