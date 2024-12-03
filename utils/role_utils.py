import traceback
import logging

logger = logging.getLogger(__name__)

import os
import config

from db.connection import DatabaseOperation
from utils import password_utils


operate = DatabaseOperation()


# 获取所有角色
async def get_all_role():
    """
    获取所有角色
    :return: 返回所有角色列表
    """
    try:
        return await operate.role_select_all()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return []
