import os
import sys
import time
import traceback
import asyncpg  # 导入 asyncpg 模块，用于异步访问 PostgreSQL 数据库
import asyncio
import logging
import config
import json

# 获取日志记录器
logger = logging.getLogger(__name__)


class ReimbursementOperate:
    # 申请报销
    async def reimbursement_apply(
        self, project_name: str, username: str, amount: float, description: str
    ):
        async with self.pool.acquire() as conn:
            try:
                # 检测用户是否有权限申请报销
                check_sql = """
                SELECT 1
                FROM projects AS p
                INNER JOIN projects_manager AS pm ON p.project_id = pm.project_id
                INNER JOIN users AS u ON pm.employee_id = u.user_id
                WHERE p.project_name = $1 AND u.username = $2 
                AND p.is_deleted = false
                """
                permission = await conn.fetchval(check_sql, project_name, username)
                if not permission:
                    # 无权限申请报销
                    return False
                # 插入报销申请
                sql = """
                    INSERT INTO reimbursement_applications 
                    (project_id, employee_id, amount, description, status, submit_date)
                    VALUES (
                    (SELECT project_id FROM projects WHERE project_name = $1), 
                    (SELECT user_id FROM users WHERE username = $2), 
                    $3, $4, $5, $6
                    );
                """
                if await conn.execute(
                    sql,
                    project_name,
                    username,
                    amount,
                    description,
                    "待审核",
                    int(time.time()),
                ):
                    return True
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
                return False

    # 报销审核
    async def reimbursement_audit(
        self, reimbursement_id: int, username: str, status: str, comments: str
    ):
        async with self.pool.acquire() as conn:
            try:
                # 检测财务人员是否有权限审核报销项目
                check_sql = """
                    SELECT 1
                    FROM reimbursement_applications AS r
                    INNER JOIN projects AS p ON r.project_id = p.project_id
                    INNER JOIN categories AS c ON p.category_id = c.category_id
                    INNER JOIN categories_manager AS cm ON c.category_id = cm.category_id
                    INNER JOIN users AS u ON cm.finance_id = u.user_id
                    WHERE r.reimbursement_id = $1 AND u.username = $2 
                    AND p.is_deleted = false AND c.is_deleted = false
                """
                permission = await conn.fetchval(check_sql, reimbursement_id, username)
                if not permission:
                    # 无权限审核
                    return False
                # 进行报销审核
                sql = """
                    UPDATE reimbursement_applications
                    SET finance_id = (SELECT user_id FROM users WHERE username = $2),
                        status = $3,
                        approve_date = $4,
                        comments = $5
                    WHERE reimbursement_id = $1;
                """
                # 进行报销审核
                if status == "已通过":
                    # 获取报销金额和项目余额
                    sql_amount = """
                        SELECT ra.amount, p.balance, p.project_id
                        FROM reimbursement_applications AS ra
                        INNER JOIN projects AS p ON ra.project_id = p.project_id
                        WHERE ra.reimbursement_id = $1;
                    """
                    result = await conn.fetchrow(sql_amount, reimbursement_id)
                    if result:
                        amount = result["amount"]
                        balance = result["balance"]
                        project_id = result["project_id"]
                        if amount <= balance:
                            await conn.execute(
                                sql,
                                reimbursement_id,
                                username,
                                status,
                                int(time.time()),
                                comments,
                            )
                            # 更新项目余额
                            sql_update_balance = """
                                UPDATE projects
                                SET balance = balance - $1
                                WHERE project_id = $2;
                            """
                            await conn.execute(sql_update_balance, amount, project_id)
                            return True
                else:
                    # 拒绝报销
                    await conn.execute(
                        sql,
                        reimbursement_id,
                        username,
                        status,
                        int(time.time()),
                        comments,
                    )
                    return True
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
            return False
