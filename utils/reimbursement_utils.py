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


# 搜索报销细明
async def search_reimbursement_info(
    page: int,  # 页码
    limit: int,  # 每页数量
    use_username: str,  # 使用用户名
    employee_username: str,  # 报销人员用户名
    employee_real_name: str,  # 报销人员真实姓名
    finance_username: str,  # 财务人员用户名
    finance_real_name: str,  # 财务人员真实姓名
    category_name: str,  # 类别名称
    project_name: str,  # 项目名称
    status: str,  # 报销状态
    role_name: str,  # 角色名称
) -> tuple:
    try:
        [
            {
                "reimbursement_id": 1,  # 报销ID
                "project_id": 1,  # 项目ID
                "project_name": "项目名称",
                "project_source": "项目来源",
                "project_is_deleted": False,  # 项目是否删除
                "category_id": 1,  # 类别ID
                "category_name": "类别名称",
                "category_is_deleted": False,  # 类别是否删除
                "employee_id": 1,  # 报销人员ID
                "employee_username": "报销人员用户名",
                "employee_real_name": "报销人员真实姓名",
                "finance_id": None,  # 财务人员ID
                "finance_username": "财务人员用户名",
                "finance_real_name": "财务人员真实姓名",
                "amount": 1000.0,  # 报销金额
                "description": "报销描述",
                "status": "待审核",  # 报销状态
                "submit_date": 1633072800,  # 提交日期
                "approve_date": None,  # 审核日期
                "comments": "审核意见",
            }
        ]
        count, list_data = await operate.reimbursement_search(
            page,
            limit,
            use_username,
            employee_username,
            employee_real_name,
            finance_username,
            finance_real_name,
            category_name,
            project_name,
            status,
            role_name,
        )
        return count, list_data
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())

    return 0, []


# 报销申请
async def reimbursement_apply(
    project_name: str, username: str, amount: float, description: str
):
    """
    报销申请
    :param project_name: 项目名称
    :param username: 用户名
    :param amount: 报销金额
    :param description: 报销描述
    :return: True or False
    """
    try:
        # 进行报销申请
        if await operate.reimbursement_apply(
            project_name, username, amount, description
        ):
            return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())

    return False


# 报销审核
async def reimbursement_audit(
    reimbursement_id: int, username: str, status: str, comments: str
):
    """
    报销审核
    :param reimbursement_id: 报销ID
    :param username: 财务人员用户名
    :param status: 报销状态
    :param comments: 审核意见
    :return: True or False
    """
    try:
        # 进行报销审核
        if await operate.reimbursement_audit(
            reimbursement_id, username, status, comments
        ):
            return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())

    return False


# 获取财务人员或报销人员的可报销项目或类别名称列表
async def get_reimbursement_name_list(username: str, role_name: str):
    """
    获取财务人员或报销人员的可报销项目或类别名称列表
    :param username: 用户名
    :param role_name: 角色名称
    :return: 项目或类别名称列表
    """
    try:
        name_list = await operate.user_allocation_name_list(username, role_name)
        return name_list
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())

    return []


# 搜索财务人员需要审核的报销列表
async def search_finance_reimbursement_list(
    page: int, limit: int, username: str, role_name: str
) -> tuple:
    try:
        category_name_list = await operate.user_allocation_name_list(
            username, role_name
        )
        count, list_data = await operate.finance_reimbursement_search(
            page, limit, category_name_list
        )
        return count, list_data
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())

    return 0, []
