import traceback
import logging

logger = logging.getLogger(__name__)

import os
import config

from db.connection import DatabaseOperation
from utils import password_utils


operate = DatabaseOperation()


# 分配报销(项目)类别
async def assign_category(category_name: str, usernames: list) -> bool:
    """
    分配报销(项目)类别
    :param category_name: 报销(项目)类别名称
    :param usernames: 用户名列表
    :return: 分配报销(项目)类别成功返回True，分配报销(项目)类别失败返回False
    """
    try:
        if await operate.category_assign(category_name, usernames):
            return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return False
