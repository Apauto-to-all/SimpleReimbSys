import traceback
import logging

logger = logging.getLogger(__name__)

import os
import config

from db.connection import DatabaseOperation
from utils import password_utils


operate = DatabaseOperation()


# 创建账户
async def create_account(
    username: str, password: str, real_name: str, role_name: str
) -> bool:
    """
    创建账户
    :param username: 用户名
    :param password: 密码
    :param real_name: 真实姓名
    :param role_name: 角色
    :return: 创建账户成功返回True，创建账户失败返回False
    """
    try:
        if operate.user_insert(
            username, password_utils.get_password(password), real_name, role_name
        ):
            return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return False


# 检查用户名是否存在
async def check_username_exist(username: str) -> bool:
    """
    判断用户名是否存在
    :param username: 用户名
    :return: 用户名存在返回True，用户名不存在返回False
    """
    try:
        if operate.user_is_exist(username):
            return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return False


# 查询用户信息
async def saerch_user_info(
    page: int, limit: int, username: str, real_name: str, role_name: str
) -> tuple:
    """
    查询用户信息
    :param page: 页码
    :param limit: 每页数量
    :param username: 用户名
    :param real_name: 真实姓名
    :param role_name: 角色
    :return: 用户信息列表
    """
    try:
        return operate.user_admin_search_list(
            page, limit, username, real_name, role_name
        )
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return 0, []
