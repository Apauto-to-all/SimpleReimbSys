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


# 用户表相关的操作
class UserTable:

    # 查询用户表的所有数据，包含角色名称
    async def user_select_one_all(self, username: str) -> dict:
        async with self.pool.acquire() as conn:
            try:
                sql = """
                SELECT users.user_id, users.username, users.password, users.real_name, users.role_id, roles.role_name
                FROM users
                LEFT JOIN roles
                ON users.role_id = roles.role_id
                WHERE users.username = $1
                """
                result = await conn.fetchrow(sql, username)
                return result
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
                return {}
