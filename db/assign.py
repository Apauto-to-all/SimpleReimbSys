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
    # 查询用户的被分配的类别或项目
    async def user_allocation_name_list(self, user_id: int, role_name: str) -> list:
        async with self.pool.acquire() as conn:
            try:
                if role_name == "财务人员":
                    sql = """
                        SELECT c.category_name
                        FROM categories_manager cm
                        JOIN categories c ON cm.category_id = c.category_id
                        WHERE cm.finance_id = $1
                    """
                    records = await conn.fetch(sql, user_id)
                    # 提取 category_name 并返回
                    category_names = [record["category_name"] for record in records]
                    return category_names

                elif role_name == "报销人员":
                    sql = """
                        SELECT p.project_name
                        FROM projects_manager pm
                        JOIN projects p ON pm.project_id = p.project_id
                        WHERE pm.employee_id = $1
                    """
                    records = await conn.fetch(sql, user_id)
                    # 提取 project_name 并返回
                    project_names = [record["project_name"] for record in records]
                    return project_names

                else:
                    return []
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
                return []

    # 分配报销(项目)类别
    async def category_assign(self, category_name: str, usernames: list):
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
                for username in usernames:
                    await conn.execute(insert_sql, username, category_name)
                return True
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
                return False

    # 删除报销(项目)类别的分配人员
    async def category_unassign(self, category_name: str, usernames: list):
        async with self.pool.acquire() as conn:
            try:
                delete_sql = """
                DELETE FROM categories_manager cm
                USING users u, categories c
                WHERE cm.finance_id = u.user_id
                AND cm.category_id = c.category_id
                AND u.username = $1
                AND c.category_name = $2
                """
                for username in usernames:
                    await conn.execute(delete_sql, username, category_name)
                return True
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
                return False
