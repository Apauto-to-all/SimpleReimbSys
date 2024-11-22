import traceback
import logging

logger = logging.getLogger(__name__)

from db.connection import DatabaseOperation
from utils import password_utils


operate = DatabaseOperation()


# 获取用户的角色
async def get_role(access_token: str) -> str:
    """
    获取用户的角色
    :param access_token: 访问令牌
    :return: 用户角色
    """
    try:
        if access_token:
            username = await password_utils.get_user_from_jwt(access_token)
            if username:
                user_dict = await operate.user_select_all(username)
                if user_dict:
                    return user_dict.get("role_name")
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return ""


# 判断是否为管理员
async def is_admin(access_token: str) -> bool:
    """
    判断是否为管理员
    :param access_token: 访问令牌
    :return: 是管理员返回True，不是管理员返回False
    """
    try:
        if access_token:
            username = await password_utils.get_user_from_jwt(access_token)
            if username:
                user_dict = await operate.user_select_all(username)
                if user_dict:
                    if user_dict.get("role_name") == "管理员":
                        return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return False
