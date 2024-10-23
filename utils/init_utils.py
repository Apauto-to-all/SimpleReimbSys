# 项目初始化
import os
import logging
from db.connection import DatabaseOperation
import config

# 获取日志记录器
logger = logging.getLogger(__name__)


# 判断项目是否是第一次运行
def is_first_run():
    if not os.path.exists(config.private_info_json):
        return True
