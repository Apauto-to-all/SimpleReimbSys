import os
import sys
import traceback
import asyncpg  # 导入 asyncpg 模块，用于异步访问 PostgreSQL 数据库
import asyncio
import logging
import config
import json

# 获取日志记录器
logger = logging.getLogger(__name__)


class RoleTable:
    async def role_select_all(self):
        async with self.pool.acquire() as conn:
            try:
                sql = """
                SELECT role_id, role_name
                FROM roles
                """
                result = await conn.fetch(sql)
                result = [dict(record) for record in result]
                return result
            except Exception as e:
                error_info = traceback.format_exc()
                logger.error(error_info)
                logger.error(e)
                return []
