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
        assign: int,
    ):
        async with self.pool.acquire() as conn:
            try:
                # 构建条件
                assign_condition = ""
                if assign == 0:
                    # 未分配，项目没有任何分配记录
                    assign_condition = "HAVING COUNT(pm.employee_id) = 0"
                elif assign == 1:
                    # 已分配，项目至少有一个分配记录
                    assign_condition = "HAVING COUNT(pm.employee_id) > 0"

                # 计数查询，加入 projects_manager 表以支持 assign 条件
                count_sql = f"""
                SELECT COUNT(*)
                FROM (
                    SELECT p.project_id
                    FROM projects p
                    JOIN categories c ON p.category_id = c.category_id
                    LEFT JOIN projects_manager pm ON p.project_id = pm.project_id
                    WHERE p.project_name ILIKE '%' || $1 || '%'
                    AND p.project_source ILIKE '%' || $2 || '%'
                    AND c.category_name ILIKE '%' || $3 || '%'
                    GROUP BY p.project_id
                    {assign_condition}
                ) sub
                """
                count = await conn.fetchval(
                    count_sql, project_name, project_source, category_name
                )
                if not count:
                    return 0, []

                # 数据查询，获取项目信息和已分配的员工ID列表
                sql = f"""
                SELECT
                    p.project_id,
                    p.project_name,
                    p.project_source,
                    p.category_id,
                    c.category_name,
                    p.total_amount,
                    p.balance,
                    COALESCE(array_agg(u.username) FILTER (WHERE u.username IS NOT NULL), '{{}}') AS username_list
                FROM projects p
                JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN projects_manager pm ON p.project_id = pm.project_id
                LEFT JOIN users u ON pm.employee_id = u.user_id
                WHERE p.project_name ILIKE '%' || $1 || '%'
                AND p.project_source ILIKE '%' || $2 || '%'
                AND c.category_name ILIKE '%' || $3 || '%'
                GROUP BY p.project_id, c.category_name, p.category_id, p.project_name, p.project_source, p.total_amount, p.balance
                {assign_condition}
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
