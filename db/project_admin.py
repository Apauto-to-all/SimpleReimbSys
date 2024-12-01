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
                sql = "SELECT * FROM project WHERE project_name = $1"
                result = await conn.fetch(sql, project_name)
                if result:
                    return True
                else:
                    return False
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
                return False
