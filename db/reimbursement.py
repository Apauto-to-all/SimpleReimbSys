import os
import sqlite3
import sys
import traceback
import asyncpg  # 导入 asyncpg 模块，用于异步访问 PostgreSQL 数据库
import asyncio
import logging
import config
import json

# 获取日志记录器
logger = logging.getLogger(__name__)


class ReimbursementTable:
    async def reimbursement_search(
        self,
        page: int,
        limit: int,
        username: str,  # 用户名
        category_name: str,  # 类别名称
        project_name: str,  # 项目名称
        status: str,  # 报销状态，待审核，已审核，已拒绝
        role_name: str,  # 角色名称
    ) -> tuple:
        async with self.pool.acquire() as conn:
            try:
                if role_name == "管理员":
                    # 管理员可以查看所有报销信息，模糊查询
                    count_sql = """
                    """
                    sql = """
                    """
                elif role_name == "财务人员":
                    # 只能查看自己负责的类别的报销信息
                    count_sql = """
                    """
                    sql = """
                    """
                elif role_name == "报销人员":
                    # 只能查看自己报销的项目的报销信息
                    count_sql = """
                    """
                    sql = """
                    """
                else:
                    return 0, []

            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())

            return 0, []
