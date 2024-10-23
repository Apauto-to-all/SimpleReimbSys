import sys
import traceback
import asyncpg  # 导入 asyncpg 模块，用于异步访问 PostgreSQL 数据库
import asyncio
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)

# 