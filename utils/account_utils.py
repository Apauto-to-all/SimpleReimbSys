from itertools import count
from re import L
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
        if await operate.user_insert(
            username,
            await password_utils.encrypt_password(password),
            real_name,
            role_name,
        ):
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
        {
            "user_id": 1,
            "username": "username",
            "real_name": "真实姓名",
            "role_id": 1,
            "role_name": "管理员，财务人员，报销人员",
            "allocation_name_list": ["category_name1", "project_name2"],
        }
        count, data = await operate.user_admin_search_list(
            page, limit, username, real_name, role_name
        )
        for record in data:
            record["allocation_name_list"] = await operate.user_allocation_name_list(
                record["username"], record["role_name"]
            )
        return count, data
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return 0, []


# 判断用户是否分配了项目类别或项目
async def search_user_allocation(username: str, role_name: str) -> bool:
    """
    判断用户是否分配了项目类别或项目
    :param username: 用户名
    :return: 分配了项目类别或项目返回True，未分配项目类别或项目返回False
    """
    try:
        if await operate.user_allocation_name_list(username, role_name):
            return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return False


# 查询用户参与的报销信息
async def check_user_reimbursement(username: str, role_name: str) -> list:
    """
    查询用户参与的报销信息
    :param username: 用户名
    :param role_name: 角色
    :return: 查询到用户参与的报销信息返回True，未查询到用户参与的报销信息返回False
    """
    try:
        result = await operate.user_reimbursement_check(username, role_name)
        return result if result else []
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return []


# 删除账户
async def delete_account(username: str) -> bool:
    """
    删除账户
    :param username: 用户名
    :return: 删除账户成功返回True，删除账户失败返回False
    """
    try:
        if await operate.user_delete(username):
            return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return False
