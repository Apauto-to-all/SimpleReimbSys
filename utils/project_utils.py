import traceback
import logging

logger = logging.getLogger(__name__)

import os
import config

from db.connection import DatabaseOperation
from utils import password_utils


operate = DatabaseOperation()

# 项目操作类


# 检测项目是否存在
async def check_project(project_name: str) -> bool:
    """
    检测项目是否存在
    :param project_name: 项目名称
    :return: 项目存在返回True，项目不存在返回False
    """
    try:
        if await operate.project_check(project_name):
            return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())

    return False


# 创建项目
async def create_project(
    project_name: str,
    project_source: str,
    category_name: str,
    total_amount: float,
    balance: float,
) -> bool:
    """
    创建项目
    :param project_name: 项目名称
    :param project_source: 项目来源
    :param category_name: 类别名称
    :param total_amount: 立项金额
    :param balance: 余额
    :return: 创建项目成功返回True，创建项目失败返回False
    """
    try:
        category_info = await operate.category_select_one_all(category_name)
        if category_info:
            category_id = category_info.get("category_id")
            if await operate.project_insert(
                project_name, project_source, category_id, total_amount, balance
            ):
                return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())

    return False
