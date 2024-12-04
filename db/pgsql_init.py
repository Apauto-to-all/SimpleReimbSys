import sys
import traceback
import asyncpg  # 导入 asyncpg 模块，用于异步访问 PostgreSQL 数据库
import asyncio
import logging

from .all_table import tables_json

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
                    error_info = traceback.format_exc()
                    logger.error(error_info)
                    return False
        except Exception as e:
            logger.error(f"连接到 PostgreSQL 服务器失败: {e}")
            error_info = traceback.format_exc()
            logger.error(error_info)
            return False

        try:  # 连接到指定数据库
            self.conn = await asyncpg.connect(
                host=self.pgsql_host,
                port=self.pgsql_port,
                user=self.pgsql_user,
                password=self.pgsql_password,
                database=self.database_name,
            )
            return True
        except Exception as e:
            logger.error(f"连接到 PostgreSQL 数据库失败: {e}")
            error_info = traceback.format_exc()
            logger.error(error_info)
            return False

    async def ensure_table_columns(self, table_name, columns):
        # 检测表是否存在
        table_exists = await self.conn.fetchval(
            """
            SELECT to_regclass($1)
            """,
            table_name,
        )
        if not table_exists:
            # 表不存在，创建表
            await self.conn.execute(
                f"""
                CREATE TABLE {table_name} (
                    {", ".join(f"{k} {v}" for k, v in columns.items() if k != "primary_key")},
                    PRIMARY KEY {columns["primary_key"]}
                )
                """
            )
        else:
            # 表存在，检查列是否存在
            existing_columns = await self.conn.fetch(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = $1
                """,
                table_name,
            )
            # 获取已存在的列名集合
            existing_column_names = {row["column_name"] for row in existing_columns}
            # 获取定义中的列名集合（不包括 primary_key）
            defined_columns = set(columns.keys()) - {"primary_key"}
            # 需要新增的列
            columns_to_add = defined_columns - existing_column_names
            # 需要删除的列
            columns_to_drop = existing_column_names - defined_columns
            # 获取主键列名
            primary_key_columns = set(columns["primary_key"].strip("()").split(","))
            primary_key_columns = {col.strip() for col in primary_key_columns}
            # 排除主键列，避免删除
            columns_to_drop -= primary_key_columns
            # 添加缺失的列
            for column_name in columns_to_add:
                column_def = columns[column_name]
                await self.conn.execute(
                    f"""
                    ALTER TABLE {table_name}
                    ADD COLUMN {column_name} {column_def}
                    """
                )
            # 删除多余的列
            for column_name in columns_to_drop:
                await self.conn.execute(
                    f"""
                    ALTER TABLE {table_name}
                    DROP COLUMN {column_name} CASCADE
                    """
                )

    async def create_table(self):
        try:
            # 创建表
            for table_name, columns in tables_json.items():
                await self.ensure_table_columns(table_name, columns)
            return True
        except Exception as e:
            logger.error(e)
            error_info = traceback.format_exc()
            logger.error(error_info)
            return False

    async def insert_init_data(self, admin_password):
        # 插入初始数据
        try:
            # 创建角色：管理员，财务人员，报销人员（如果不存在）
            roles = ["管理员", "财务人员", "报销人员"]
            for role in roles:
                await self.conn.execute(
                    """
                    INSERT INTO roles (role_name) 
                    VALUES ($1)
                    ON CONFLICT (role_name) DO NOTHING
                """,
                    role,
                )

            # 创建一个管理员账户（如果不存在）
            await self.conn.execute(
                """
                INSERT INTO users (username, password, real_name, role_id)
                VALUES ($1, $2, $3, (SELECT role_id FROM roles WHERE role_name = $4))
                ON CONFLICT (username) DO NOTHING
            """,
                "admin",
                admin_password,
                "管理员",
                "管理员",
            )

            await self.conn.close()
            return True
        except Exception as e:
            logger.error(e)
            error_info = traceback.format_exc()
            logger.error(error_info)
            return False
