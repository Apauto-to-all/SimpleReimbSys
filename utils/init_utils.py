# 项目初始化
import logging
import os
import config
import json
from db.pgsql_init import PgsqlInit
from utils import password_utils

# 获取日志记录器
logger = logging.getLogger(__name__)

pg_init = PgsqlInit()  # 创建 PgsqlInit 对象


# 测试是否能够连接数据库，创建表，写入数据库连接信息到配置文件
async def is_connectable(
    pgsql_host, pgsql_port, pgsql_user, pgsql_password, database_name
):
    if await pg_init.is_connectable(
        pgsql_host, pgsql_port, pgsql_user, pgsql_password, database_name
    ):  # 测试是否能够连接数据库
        await pg_init.create_table()  # 创建表
        # 插入初始数据
        # 自动生成一个随机密码
        admin_password = "admin"
        hash_password = await password_utils.encrypt_password(admin_password)
        await pg_init.insert_init_data(hash_password)
        # 生成密匙的算法
        import secrets

        private_info = {
            "pgsql_host": pgsql_host,
            "pgsql_port": pgsql_port,
            "pgsql_user": pgsql_user,
            "pgsql_password": pgsql_password,
            "database_name": database_name,
            "SECRET_KEY": secrets.token_hex(32),
            "login_time_minute": 36000,  # 登入时间分钟
        }
        with open(config.private_info_json, "w") as f:
            json.dump(private_info, f, indent=4, ensure_ascii=False)
        logger.info("写入数据库连接信息到配置文件")
        return True
    return False


# 验证数据库连接信息
def check_private_info():
    """
    验证数据库连接信息，验证private_info.json文件
    :return: True 验证通过，False 验证失败
    """
    if not os.path.exists(config.private_info_json):
        logger.warning(f"配置文件不存在")
        return False
    try:
        with open(config.private_info_json, "r") as f:
            private_info = json.load(f)
        if (
            private_info.get("pgsql_host")
            and private_info.get("pgsql_port")
            and private_info.get("pgsql_user")
            and private_info.get("pgsql_password")
            and private_info.get("database_name")
            and private_info.get("SECRET_KEY")
            and private_info.get("login_time_minute")
        ):
            return True
        return False
    except Exception as e:
        logger.error(e)
        return False
