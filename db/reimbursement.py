import os
import sqlite3
import sys
import traceback
import asyncpg  # 导入 asyncpg 模块，用于异步访问 PostgreSQL 数据库
import asyncio
import logging
import config
import json

# 获取日志记录器
logger = logging.getLogger(__name__)


class ReimbursementTable:
    async def reimbursement_search(
        self,
        page: int,
        limit: int,
        use_username: str,  # 当前登录的用户名
        employee_username: str,  # 报销人员用户名
        employee_real_name: str,  # 报销人员真实姓名
        finance_username: str,  # 财务人员用户名
        finance_real_name: str,  # 财务人员真实姓名
        category_name: str,  # 类别名称
        project_name: str,  # 项目名称
        status: str,  # 报销状态，待审核，已审核，已拒绝
        role_name: str,  # 角色名称
    ) -> tuple:
        async with self.pool.acquire() as conn:
            try:
                offset = (page - 1) * limit  # 计算偏移量

                if role_name == "管理员":
                    # 管理员可以查看所有报销信息，模糊查询
                    count_sql = f"""
                    SELECT COUNT(*) FROM reimbursement_applications AS r
                    LEFT JOIN projects AS p ON r.project_id = p.project_id
                    LEFT JOIN categories AS c ON p.category_id = c.category_id
                    LEFT JOIN users AS eu ON r.employee_id = eu.user_id
                    LEFT JOIN users AS fu ON r.finance_id = fu.user_id
                    WHERE eu.username ILIKE '%' || $1 || '%'
                    AND eu.real_name ILIKE '%' || $2 || '%'
                    AND fu.username ILIKE '%' || $3 || '%'
                    AND fu.real_name ILIKE '%' || $4 || '%'
                    AND c.category_name ILIKE '%' || $5 || '%'
                    AND p.project_name ILIKE '%' || $6 || '%'
                    AND r.status ILIKE '%' || $7 || '%'
                    """
                    sql = f"""
                    SELECT
                        r.*,
                        p.project_name,
                        p.project_source,
                        p.is_deleted AS project_is_deleted,
                        c.category_id,
                        c.category_name,
                        c.is_deleted AS category_is_deleted,
                        eu.username AS employee_username,
                        eu.real_name AS employee_real_name,
                        fu.username AS finance_username,
                        fu.real_name AS finance_real_name
                    FROM reimbursement_applications AS r
                    LEFT JOIN projects AS p ON r.project_id = p.project_id
                    LEFT JOIN categories AS c ON p.category_id = c.category_id
                    LEFT JOIN users AS eu ON r.employee_id = eu.user_id
                    LEFT JOIN users AS fu ON r.finance_id = fu.user_id
                    WHERE eu.username ILIKE '%' || $1 || '%'
                    AND eu.real_name ILIKE '%' || $2 || '%'
                    AND fu.username ILIKE '%' || $3 || '%'
                    AND fu.real_name ILIKE '%' || $4 || '%'
                    AND c.category_name ILIKE '%' || $5 || '%'
                    AND p.project_name ILIKE '%' || $6 || '%'
                    AND r.status ILIKE '%' || $7 || '%'
                    ORDER BY r.reimbursement_id DESC
                    LIMIT $8 OFFSET $9
                    """
                    params = [
                        employee_username,
                        employee_real_name,
                        finance_username,
                        finance_real_name,
                        category_name,
                        project_name,
                        status,
                        limit,
                        offset,
                    ]
                elif role_name == "财务人员":
                    # 财务人员只能查看自己审核过的报销信息
                    count_sql = f"""
                    SELECT COUNT(*) FROM reimbursement_applications AS r
                    LEFT JOIN projects AS p ON r.project_id = p.project_id
                    LEFT JOIN categories AS c ON p.category_id = c.category_id
                    LEFT JOIN users AS eu ON r.employee_id = eu.user_id
                    WHERE r.finance_id = (SELECT user_id FROM users WHERE username = $1)
                    AND eu.username ILIKE '%' || $2 || '%'
                    AND eu.real_name ILIKE '%' || $3 || '%'
                    AND c.category_name ILIKE '%' || $4 || '%'
                    AND p.project_name ILIKE '%' || $5 || '%'
                    AND r.status ILIKE '%' || $6 || '%'
                    """
                    sql = f"""
                    SELECT
                        r.*,
                        p.project_name,
                        p.project_source,
                        p.is_deleted AS project_is_deleted,
                        c.category_id,
                        c.category_name,
                        c.is_deleted AS category_is_deleted,
                        eu.username AS employee_username,
                        eu.real_name AS employee_real_name,
                        fu.username AS finance_username,
                        fu.real_name AS finance_real_name
                    FROM reimbursement_applications AS r
                    LEFT JOIN projects AS p ON r.project_id = p.project_id
                    LEFT JOIN categories AS c ON p.category_id = c.category_id
                    LEFT JOIN users AS eu ON r.employee_id = eu.user_id
                    LEFT JOIN users AS fu ON r.finance_id = fu.user_id
                    WHERE r.finance_id = (SELECT user_id FROM users WHERE username = $1)
                    AND eu.username ILIKE '%' || $2 || '%'
                    AND eu.real_name ILIKE '%' || $3 || '%'
                    AND c.category_name ILIKE '%' || $4 || '%'
                    AND p.project_name ILIKE '%' || $5 || '%'
                    AND r.status ILIKE '%' || $6 || '%'
                    ORDER BY r.reimbursement_id DESC
                    LIMIT $7 OFFSET $8
                    """
                    params = [
                        use_username,
                        employee_username,
                        employee_real_name,
                        category_name,
                        project_name,
                        status,
                        limit,
                        offset,
                    ]
                elif role_name == "报销人员":
                    # 报销人员只能查看自己提交的报销信息
                    count_sql = f"""
                    SELECT COUNT(*) FROM reimbursement_applications AS r
                    LEFT JOIN projects AS p ON r.project_id = p.project_id
                    LEFT JOIN categories AS c ON p.category_id = c.category_id
                    LEFT JOIN users AS fu ON r.finance_id = fu.user_id
                    WHERE r.employee_id = (SELECT user_id FROM users WHERE username = $1)
                    AND fu.username ILIKE '%' || $2 || '%'
                    AND fu.real_name ILIKE '%' || $3 || '%'
                    AND c.category_name ILIKE '%' || $4 || '%'
                    AND p.project_name ILIKE '%' || $5 || '%'
                    AND r.status ILIKE '%' || $6 || '%'
                    """
                    sql = f"""
                    SELECT
                        r.*,
                        p.project_name,
                        p.project_source,
                        p.is_deleted AS project_is_deleted,
                        c.category_id,
                        c.category_name,
                        c.is_deleted AS category_is_deleted,
                        eu.username AS employee_username,
                        eu.real_name AS employee_real_name,
                        fu.username AS finance_username,
                        fu.real_name AS finance_real_name
                    FROM reimbursement_applications AS r
                    LEFT JOIN projects AS p ON r.project_id = p.project_id
                    LEFT JOIN categories AS c ON p.category_id = c.category_id
                    LEFT JOIN users AS eu ON r.employee_id = eu.user_id
                    LEFT JOIN users AS fu ON r.finance_id = fu.user_id
                    WHERE r.employee_id = (SELECT user_id FROM users WHERE username = $1)
                    AND fu.username ILIKE '%' || $2 || '%'
                    AND fu.real_name ILIKE '%' || $3 || '%'
                    AND c.category_name ILIKE '%' || $4 || '%'
                    AND p.project_name ILIKE '%' || $5 || '%'
                    AND r.status ILIKE '%' || $6 || '%'
                    ORDER BY r.reimbursement_id DESC
                    LIMIT $7 OFFSET $8
                    """
                    params = [
                        use_username,
                        finance_username,
                        finance_real_name,
                        category_name,
                        project_name,
                        status,
                        limit,
                        offset,
                    ]
                else:
                    return 0, []

                # 执行查询
                count = await conn.fetchval(count_sql, *params[:-2])
                if not count:
                    return 0, []

                records = await conn.fetch(sql, *params)
                # 将记录转换为列表
                data = [dict(record) for record in records]
                return count, data
            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
                return 0, []
