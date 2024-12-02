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


class ProjectAdminOperation:
    # 检测项目是否存在
    async def project_check(self, project_name: str) -> bool:
        async with self.pool.acquire() as conn:
            try:
                sql = "SELECT * FROM projects WHERE project_name = $1"
                result = await conn.fetch(sql, project_name)
                if result:
                    return True
                else:
                    return False
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
                return False

    # 创建项目
    async def project_insert(
        self,
        project_name: str,
        project_source: str,
        category_id: int,
        total_amount: float,
        balance: float,
    ) -> bool:
        async with self.pool.acquire() as conn:
            try:
                sql = """
                    INSERT INTO projects (project_name, project_source, category_id, total_amount, balance)
                    VALUES ($1, $2, $3, $4, $5)
                """
                await conn.execute(
                    sql,
                    project_name,
                    project_source,
                    category_id,
                    total_amount,
                    balance,
                )
                return True
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
                return False

    # 搜索项目信息
    async def project_search(
        self,
        page: int,
        limit: int,
        project_name: str,
        category_name: str,
        project_source: str,
    ):
        async with self.pool.acquire() as conn:
            try:
                # 计数查询，加入 categories 表以支持 category_name 的模糊搜索
                count_sql = """
                SELECT COUNT(*)
                FROM projects p
                JOIN categories c ON p.category_id = c.category_id
                WHERE p.project_name ILIKE '%' || $1 || '%' 
                AND p.project_source ILIKE '%' || $2 || '%' 
                AND c.category_name ILIKE '%' || $3 || '%'
                """
                count = await conn.fetchval(
                    count_sql, project_name, project_source, category_name
                )
                if not count:
                    return 0, []

                # 数据查询，加入 categories 表以支持 category_name 的模糊搜索
                sql = """
                SELECT p.project_id, p.project_name, p.project_source, p.category_id, c.category_name, p.total_amount, p.balance
                FROM projects p
                JOIN categories c ON p.category_id = c.category_id
                WHERE p.project_name ILIKE '%' || $1 || '%' 
                AND p.project_source ILIKE '%' || $2 || '%' 
                AND c.category_name ILIKE '%' || $3 || '%'
                ORDER BY p.project_id
                LIMIT $4
                OFFSET $5
                """
                result = await conn.fetch(
                    sql,
                    project_name,
                    project_source,
                    category_name,
                    limit,
                    (page - 1) * limit,
                )
                result = [dict(record) for record in result]
                return count, result
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
                return 0, []
