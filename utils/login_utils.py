import traceback
import logging

logger = logging.getLogger(__name__)

from db.connection import DatabaseOperation
from utils import password_utils


operate = DatabaseOperation()


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


# 判断是否登入
async def is_login(access_token: str) -> bool:
    """
    判断是否登入
    :param access_token: 访问令牌
    :return: 登入返回True，未登入返回False
    """
    try:
        if access_token:
            username = await password_utils.get_user_from_jwt(access_token)
            if username:
                if await operate.user_is_exist(username):
                    return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return False


# 用户登入，验证用户名和密码
async def verify_login(username: str, password: str) -> bool:
    """
    用户登入，验证用户名和密码
    :param username: 用户名
    :param password: 密码
    :return: 登入成功返回True，登入失败返回False
    """
    try:
        user_dict = await operate.user_select_all(username)
        if user_dict:
            if await password_utils.verify_password(
                user_dict.get("password"), password
            ):
                return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return False
