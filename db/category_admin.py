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
    async def category_search(
        self, page: int, limit: int, category_name: str, assign: int
    ):
        async with self.pool.acquire() as conn:
            try:
                # 构建条件
                assign_condition = ""
                if assign == 0:
                    assign_condition = "HAVING COUNT(cm.finance_id) = 0"
                elif assign == 1:
                    assign_condition = "HAVING COUNT(cm.finance_id) > 0"

                # 查询总数
                count_sql = f"""
                SELECT COUNT(*)
                FROM (
                    SELECT c.category_id
                    FROM categories c
                    LEFT JOIN categories_manager cm ON c.category_id = cm.category_id
                    WHERE c.category_name ILIKE '%' || $1 || '%'
                    GROUP BY c.category_id
                    {assign_condition}
                ) sub
                """
                count = await conn.fetchval(count_sql, category_name)
                if not count:
                    return 0, []

                # 查询类别信息和财务人员列表
                sql = f"""
                SELECT
                    c.category_id,
                    c.category_name,
                    COALESCE(array_agg(cm.finance_id) FILTER (WHERE cm.finance_id IS NOT NULL), '{{}}') AS finance_id_list
                FROM categories c
                LEFT JOIN categories_manager cm ON c.category_id = cm.category_id
                WHERE c.category_name ILIKE '%' || $1 || '%'
                GROUP BY c.category_id
                {assign_condition}
                ORDER BY c.category_id
                LIMIT $2 OFFSET $3
                """
                result = await conn.fetch(sql, category_name, limit, (page - 1) * limit)
                result = [dict(record) for record in result]
                return count, result
            except Exception as e:
                error_info = traceback.format_exc()
                logger.error(error_info)
                logger.error(e)
                return 0, []

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
