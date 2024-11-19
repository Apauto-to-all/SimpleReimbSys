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


class UsersAdminOperation:
    # 创建用户
    async def user_insert(
        self, username: str, password: str, real_name: str, role_name: str
    ):
        async with self.pool.acquire() as conn:
            try:
                sql = """
                INSERT INTO users (username, password, real_name, role_id)
                VALUES ($1, $2, $3, (SELECT role_id FROM roles WHERE role_name = $4))
                ON CONFLICT (username) DO NOTHING
                """
                await conn.execute(sql, username, password, real_name, role_name)
                return True
            except Exception as e:
                error_info = traceback.format_exc()
                logger.error(error_info)
                logger.error(e)
                return False
