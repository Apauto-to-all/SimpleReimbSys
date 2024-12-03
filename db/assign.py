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


class AssignOperation:
    # 分配报销(项目)类别
    async def category_assign(self, category_name: str, username: str):
        async with self.pool.acquire() as conn:
            try:
                insert_sql = """
                INSERT INTO categories_manager (finance_id, category_id)
                SELECT u.user_id, c.category_id
                FROM users u
                JOIN categories c ON c.category_name = $2
                WHERE u.username = $1
                ON CONFLICT DO NOTHING
                """
                await conn.execute(insert_sql, username, category_name)
                return True

            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
                return False
