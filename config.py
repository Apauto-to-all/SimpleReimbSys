import logging, os, datetime

from logging.handlers import TimedRotatingFileHandler

# 全局配置文件

# 项目运行的主机和端口
host = "localhost"
port = 19791

# 私人信息，如数据库密码等
private_info_json = "private_info.json"

# 创建日志目录
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    handlers=[
        TimedRotatingFileHandler(
            filename=os.path.join(
                log_directory, datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
            ),
            when="midnight",  # 每天午夜创建一个新的日志文件
            interval=1,  # 间隔1天
            backupCount=20,  # 保留最近7天的日志文件
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)


logging.info("日志记录器初始化完成")
