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
    page: int,
    limit: int,
    use_username: str,
    employee_username: str,
    employee_real_name: str,
    finance_username: str,
    finance_real_name: str,
    category_name: str,
    project_name: str,
    status: str,
    role_name: str,
):
    """
    搜索报销细明信息
    :param page: 页码
    :param limit: 每页数量

    :param use_username: 当前登入的用户名

    :param employee_username: 报销人员用户名
    :param employee_real_name: 报销人员真实姓名

    :param finance_username: 财务人员用户名
    :param finance_real_name: 财务人员真实姓名

    :param category_name: 类别名称
    :param project_name: 项目名称
    :param status: 报销状态
    :param role_name: 角色名称

    :return: 总数，列表数据
    """
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


# 检查财务人员是否有权限审核报销项目
async def check_finance_reimbursement(reimbursement_id: int, username: str):
    """
    检查财务人员是否有权限审核报销项目
    :param username: 财务人员用户名
    :param reimbursement_id: 报销ID
    :return: True or False
    """
    try:
        # 检查财务人员是否有权限审核报销项目
        if await operate.check_finance_reimbursement(reimbursement_id, username):
            return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())

    return False
