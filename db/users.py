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
    # 查询用户表的所有数据
    async def user_select_all(self, username: str) -> dict:
        async with self.pool.acquire() as conn:
            try:
                sql = """
                SELECT * FROM users WHERE username = $1;
                """
                result = await conn.fetchrow(sql, username)
                return result
            except Exception as e:
                error_info = traceback.format_exc()
                logger.error(error_info)
                logger.error(e)
                return {}

    # 查询用户是否存在
    async def user_is_exist(self, username: str):
        async with self.pool.acquire() as conn:
            try:
                sql = """
                SELECT username FROM users WHERE username = $1;
                """
                result = await conn.fetch(sql, username)
                if result:
                    return True
                return False
            except Exception as e:
                error_info = traceback.format_exc()
                logger.error(error_info)
                logger.error(e)
                return False
