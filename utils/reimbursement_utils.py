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


async def search_reimbursement_info(
    page: int,
    limit: int,
    username: str,
    category_name: str,
    project_name: str,
    status: str,
    role_name: str,
):
    """
    搜索报销细明信息
    :param page: 页码
    :param limit: 每页数量
    :param username: 用户名
    :param category_name: 类别名称
    :param project_name: 项目名称
    :param status: 报销状态
    :param role_name: 角色名称
    :return: 总数，列表数据
    """
    try:
        count, list_data = await operate.reimbursement_search(
            page,
            limit,
            username,
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
