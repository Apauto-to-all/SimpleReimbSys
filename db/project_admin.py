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
    # 获取一个项目的所有信息
    async def project_select_one_all(self, project_name: str):
        async with self.pool.acquire() as conn:
            try:
                sql = """
                SELECT project_id, project_name, project_source, category_id, total_amount, balance, is_deleted
                FROM projects
                WHERE project_name = $1
                """
                result = await conn.fetch(sql, project_name)
                return result
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
                return []

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
                    AND p.is_deleted = false
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
                AND p.is_deleted = false
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

    # 搜索项目分配的报销人员
    async def project_search_assign_users(self, project_name: str):
        async with self.pool.acquire() as conn:
            try:
                sql = """
                SELECT u.user_id, u.username
                FROM users u
                JOIN projects_manager pm ON u.user_id = pm.employee_id
                JOIN projects p ON pm.project_id = p.project_id
                WHERE p.project_name = $1
                AND p.is_deleted = false
                """
                result = await conn.fetch(sql, project_name)
                return [dict(record) for record in result]
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
                return []

    # 删除项目
    async def project_delete(self, project_name: str):
        async with self.pool.acquire() as conn:
            try:
                # 首先检测在reimbursement_applications表中是否存在该类别，如果存在，设置is_deleted删除
                check_sql = """
                SELECT EXISTS (
                    SELECT 1
                    FROM reimbursement_applications ra
                    JOIN projects p ON ra.project_id = p.project_id
                    WHERE p.project_name = $1
                )
                """
                check_result = await conn.fetchval(check_sql, project_name)
                if check_result:
                    # 如果存在，设置is_deleted删除
                    sql = """
                    UPDATE projects
                    SET is_deleted = true
                    WHERE project_name = $1
                    """
                else:
                    # 如果不存在，直接删除
                    sql = """
                    DELETE FROM projects
                    WHERE project_name = $1
                    """
                await conn.execute(sql, project_name)
                return True
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
                return False
