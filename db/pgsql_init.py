import sys
import traceback
import asyncpg  # 导入 asyncpg 模块，用于异步访问 PostgreSQL 数据库
import asyncio
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)


# 连接数据库，创建表
class PgsqlInit:
    def __init__(self):
        self.pgsql_host = None
        self.pgsql_port = None
        self.pgsql_user = None
        self.pgsql_password = None
        self.database_name = None
        self.conn = None

    # 测试是否能够连接数据库
    async def is_connectable(
        self, pgsql_host, pgsql_port, pgsql_user, pgsql_password, database_name
    ):
        self.pgsql_host = pgsql_host
        self.pgsql_port = pgsql_port
        self.pgsql_user = pgsql_user
        self.pgsql_password = pgsql_password
        self.database_name = database_name
        try:  # 连接服务器，不指定数据库
            conn = await asyncpg.connect(
                host=pgsql_host,
                port=pgsql_port,
                user=pgsql_user,
                password=pgsql_password,
            )
            logger.info("成功连接到 PostgreSQL 服务器")

            try:  # 连接到指定数据库
                await conn.close()
                conn = await asyncpg.connect(
                    host=pgsql_host,
                    port=pgsql_port,
                    user=pgsql_user,
                    password=pgsql_password,
                    database=database_name,
                )
                logger.info(f"成功连接到 PostgreSQL 数据库 {database_name}")
            except Exception as e:
                logger.warning(f"无法连接到数据库 {database_name}，尝试创建数据库")
                try:  # 创建数据库
                    await conn.close()
                    conn = await asyncpg.connect(
                        host=pgsql_host,
                        port=pgsql_port,
                        user=pgsql_user,
                        password=pgsql_password,
                    )
                    # 创建数据库，并连接到新创建的数据库
                    await conn.execute(f"CREATE DATABASE {database_name}")
                    # 重新连接到新创建的数据库
                    await conn.close()
                    conn = await asyncpg.connect(
                        host=pgsql_host,
                        port=pgsql_port,
                        user=pgsql_user,
                        password=pgsql_password,
                        database=database_name,
                    )
                    logger.info(f"成功连接到新创建的数据库 {database_name}")
                    await conn.close()
                except Exception as e:
                    logger.error(f"连接到 PostgreSQL 服务器失败: {e}")
                    return False
        except Exception as e:
            logger.error(f"连接到 PostgreSQL 服务器失败: {e}")
            return False

        self.conn = await asyncpg.connect(
            host=self.pgsql_host,
            port=self.pgsql_port,
            user=self.pgsql_user,
            password=self.pgsql_password,
            database=self.database_name,
        )
        return True

    # 创建表
    async def create_table(self):
        # 创建表的 SQL 语句
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            
        );
        """
        try:
            # 执行 SQL 语句
            await self.conn.execute(sql)
            return True
        except Exception as e:
            logger.error(e)
            return False
