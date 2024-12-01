import traceback
import logging

logger = logging.getLogger(__name__)

import os
import config

from db.connection import DatabaseOperation
from utils import password_utils


operate = DatabaseOperation()

# 报销(项目)类别工具类


# 检测报销(项目)类别是否存在
async def check_category(category_name: str) -> bool:
    """
    检测报销(项目)类别是否存在
    :param category_name: 报销(项目)类别名称
    :return: 报销(项目)类别存在返回True，报销(项目)类别不存在返回False
    """
    try:
        if await operate.category_check(category_name):
            return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return False


# 创建报销(项目)类别
async def create_category(category_name: str) -> bool:
    """
    创建报销(项目)类别
    :param category_name: 报销(项目)类别名称
    :return: 创建报销(项目)类别成功返回True，创建报销(项目)类别失败返回False
    """
    try:
        if await operate.category_insert(category_name):
            return True
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return False


# 搜索报销(项目)类别信息
async def search_category_info(page: int, limit: int, category_name: str) -> tuple:
    """
    搜索报销(项目)类别信息
    :param page: 页码
    :param limit: 每页显示数量
    :param category_name: 报销(项目)类别名称
    :return: 返回查询到的报销(项目)类别数量和列表
    """
    count = 0
    list_data = []
    try:
        count, list_data = await operate.category_search(page, limit, category_name)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return count, list_data


# 获取所有报销(项目)类别
async def search_all_category() -> list:
    """
    获取所有报销(项目)类别
    :return: 返回所有报销(项目)类别列表
    """
    list_data = []
    try:
        list_data = await operate.category_search_all()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
    return list_data
