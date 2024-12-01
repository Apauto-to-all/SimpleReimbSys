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


class CategoryAdminOperation:
    # 获取报销(项目)类别某一个类型的所有信息
    async def category_select_one_all(self, category_name: str):
        async with self.pool.acquire() as conn:
            try:
                sql = """
                SELECT category_id, category_name
                FROM categories
                WHERE category_name = $1
                """
                result = await conn.fetchrow(sql, category_name)
                return result
            except Exception as e:
                error_info = traceback.format_exc()
                logger.error(error_info)
                logger.error(e)
                return []

    # 搜索报销(项目)类别信息
    async def category_search(self, page: int, limit: int, category_name: str):
        async with self.pool.acquire() as conn:
            try:
                count_sql = """
                SELECT COUNT(*)
                FROM categories
                WHERE category_name ILIKE '%' || $1 || '%'
                """
                count = await conn.fetchval(count_sql, category_name)
                if not count:
                    return 0, []
                sql = """
                SELECT category_id, category_name
                FROM categories
                WHERE category_name ILIKE '%' || $1 || '%'
                ORDER BY category_id
                LIMIT $2
                OFFSET $3
                """
                result = await conn.fetch(sql, category_name, limit, (page - 1) * limit)
                result = [dict(record) for record in result]
                return count, result
            except Exception as e:
                error_info = traceback.format_exc()
                logger.error(error_info)
                logger.error(e)
                return 0, []

    # 检测报销(项目)类别是否存在
    async def category_check(self, category_name: str) -> bool:
        async with self.pool.acquire() as conn:
            try:
                sql = """
                SELECT *
                FROM categories
                WHERE category_name = $1
                """
                result = await conn.fetchval(sql, category_name)
                if result:
                    return True
                return False
            except Exception as e:
                error_info = traceback.format_exc()
                logger.error(error_info)
                logger.error(e)
                return False

    # 创建报销(项目)类别，如果类别已存在，不操作
    async def category_insert(self, category_name: str):
        async with self.pool.acquire() as conn:
            try:
                sql = """
                INSERT INTO categories (category_name)
                VALUES ($1)
                ON CONFLICT (category_name) DO NOTHING
                """
                await conn.execute(sql, category_name)
                return True
            except Exception as e:
                error_info = traceback.format_exc()
                logger.error(error_info)
                logger.error(e)
                return False

    # 获取所有报销(项目)类别
    async def category_search_all(self):
        async with self.pool.acquire() as conn:
            try:
                sql = """
                SELECT category_id, category_name
                FROM categories
                ORDER BY category_id
                """
                result = await conn.fetch(sql)
                result = [dict(record) for record in result]
                return result
            except Exception as e:
                error_info = traceback.format_exc()
                logger.error(error_info)
                logger.error(e)
                return []
