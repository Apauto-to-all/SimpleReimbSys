# 项目初始化
import importlib
import logging
import os
import config
from db.pgsql_init import PgsqlInit
from utils import password_utils

# 获取日志记录器
logger = logging.getLogger(__name__)

pg_init = PgsqlInit()  # 创建 PgsqlInit 对象


# 测试是否能够连接数据库，创建表，写入数据库连接信息到配置文件
async def is_connectable(
    pgsql_host, pgsql_port, pgsql_user, pgsql_password, database_name
):
    try:
        private_info_path = config.private_info_name + ".py"  # 配置文件路径
        if await pg_init.is_connectable(
            pgsql_host, pgsql_port, pgsql_user, pgsql_password, database_name
        ):
            await pg_init.create_table()  # 创建表
            # 插入初始数据
            # 自动生成一个随机密码
            admin_password = "admin"
            hash_password = await password_utils.encrypt_password(admin_password)
            await pg_init.insert_init_data(hash_password)
            # 生成密匙的算法
            import secrets

            private_info = {
                "pgsql_host": pgsql_host,  # PostgreSQL 数据库的主机名
                "pgsql_port": pgsql_port,  # PostgreSQL 数据库的端口
                "pgsql_user": pgsql_user,  # PostgreSQL 数据库的用户名
                "pgsql_password": pgsql_password,  # PostgreSQL 数据库的密码
                "database_name": database_name,  # 数据库名
                "SECRET_KEY": secrets.token_hex(32),  # 密匙
                "login_time_minute": 36000,  # 登入时间分钟
            }
            comments = {
                "pgsql_host": "PostgreSQL 数据库的主机名",
                "pgsql_port": "PostgreSQL 数据库的端口",
                "pgsql_user": "PostgreSQL 数据库的用户名",
                "pgsql_password": "PostgreSQL 数据库的密码",
                "database_name": "数据库名",
                "SECRET_KEY": "密匙",
                "login_time_minute": "登入时间分钟",
            }

            with open(private_info_path, "w", encoding="utf-8") as f:
                for key, value in private_info.items():
                    comment = comments.get(key, "")
                    if isinstance(value, str):
                        f.write(f"# {comment}\n{key} = '{value}'\n\n")
                    else:
                        f.write(f"# {comment}\n{key} = {value}\n\n")
            logger.info("写入数据库连接信息到配置文件")
            return True
    except Exception as e:
        logger.error(f"写入数据库连接信息到配置文件时发生错误: {e}")

    # 如果配置文件存在，但是连接数据库失败，就删除配置文件
    if os.path.exists(private_info_path):
        os.remove(private_info_path)
    return False


def check_private_info():
    """
    验证数据库连接信息，验证private_info.py文件
    :return: True 验证通过，False 验证失败
    """
    private_info_path = config.private_info_name + ".py"  # 配置文件路径
    if not os.path.exists(private_info_path):
        logger.warning("配置文件不存在")
        return False

    try:
        # 动态导入private_info.py模块
        spec = importlib.util.spec_from_file_location("private_info", private_info_path)
        private_info = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(private_info)

        required_attributes = [
            "pgsql_host",
            "pgsql_port",
            "pgsql_user",
            "pgsql_password",
            "database_name",
            "SECRET_KEY",
            "login_time_minute",
        ]

        for attr in required_attributes:
            if not hasattr(private_info, attr):
                logger.warning(f"配置缺少必要的属性: {attr}")
                return False

        # 可选：进一步验证属性的类型或值
        if not isinstance(private_info.pgsql_port, int):
            logger.warning("pgsql_port 应为整数")
            return False
        if not isinstance(private_info.login_time_minute, int):
            logger.warning("login_time_minute 应为整数")
            return False
        # 其他类型或值的验证可以根据需要添加

        logger.info("配置文件验证通过")
        return True

    except Exception as e:
        logger.error(f"验证配置文件时发生错误: {e}")
        return False
