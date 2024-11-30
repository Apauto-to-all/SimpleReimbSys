# 关于用户的工具
import traceback
import logging

logger = logging.getLogger(__name__)

import os
import config

from db.connection import DatabaseOperation
from utils import password_utils


operate = DatabaseOperation()


# 根据用户名查询所有的用户信息
async def user_select_all(access_token: str) -> dict:
    """
    根据用户名查询所有的用户信息
    :param access_token: 访问令牌
    :return: 用户信息
    """
    try:
        if access_token:
            username = await password_utils.get_user_from_jwt(access_token)
            if username:
                user_dict = await operate.user_select_all(username)
                {
                    "user_id": "1",
                    "username": "admin",
                    "password": "加密后的密码",
                    "real_name": "管理员",
                    "role_id": "1",
                    "role_name": "管理员",
                }
                if user_dict:
                    return user_dict
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return {}
