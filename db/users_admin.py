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

    # 查询所有用户，模糊匹配, 返回总数和数据
    async def user_admin_search_list(
        self, page: int, limit: int, username: str, real_name: str, role_name: str
    ) -> tuple:
        async with self.pool.acquire() as conn:
            try:
                count_sql = """
                SELECT COUNT(*)
                FROM users
                LEFT JOIN roles
                ON users.role_id = roles.role_id
                WHERE ($1 = '' OR users.username ILIKE '%' || $1 || '%')
                AND ($2 = '' OR users.real_name ILIKE '%' || $2 || '%')
                AND ($3 = '' OR roles.role_name ILIKE '%' || $3 || '%')
                """
                count = await conn.fetchval(count_sql, username, real_name, role_name)
                if not count:
                    return 0, []

                sql = """
                SELECT users.user_id, users.username, users.real_name, users.role_id, roles.role_name
                FROM users
                LEFT JOIN roles
                ON users.role_id = roles.role_id
                WHERE ($1 = '' OR users.username ILIKE '%' || $1 || '%')
                AND ($2 = '' OR users.real_name ILIKE '%' || $2 || '%')
                AND ($3 = '' OR roles.role_name ILIKE '%' || $3 || '%')
                LIMIT $4 OFFSET $5
                """
                data = await conn.fetch(
                    sql, username, real_name, role_name, limit, (page - 1) * limit
                )
                data = [dict(record) for record in data]
                return count, data
            except Exception as e:
                error_info = traceback.format_exc()
                logger.error(error_info)
                logger.error(e)
                return 0, []

    # 检测用户是否参与报销
    async def user_reimbursement_check(self, username: str, role_name: str) -> bool:
        async with self.pool.acquire() as conn:
            try:
                if role_name == "财务人员":
                    sql = """
                    SELECT 1
                    FROM reimbursement_applications ra
                    JOIN users u ON ra.finance_id = u.user_id
                    WHERE u.username = $1
                    LIMIT 1
                    """
                elif role_name == "报销人员":
                    sql = """
                    SELECT 1
                    FROM reimbursement_applications ra
                    JOIN users u ON ra.employee_id = u.user_id
                    WHERE u.username = $1
                    LIMIT 1
                    """
                else:
                    return False

                if await conn.fetch(sql, username):
                    return True
            except Exception as e:
                error_info = traceback.format_exc()
                logger.error(error_info)
                logger.error(e)

            return False

    # 删除用户
    async def user_delete(self, username: str):
        async with self.pool.acquire() as conn:
            try:
                sql = """
                DELETE FROM users
                WHERE username = $1
                """
                await conn.execute(sql, username)
                return True
            except Exception as e:
                error_info = traceback.format_exc()
                logger.error(error_info)
                logger.error(e)
                return False
