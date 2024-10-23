import importlib
import os
import sys
import subprocess
from fastapi import FastAPI, Cookie  # 导入 FastAPI 框架
import uvicorn
from fastapi.responses import (
    FileResponse,
    HTMLResponse,  # 用于返回 HTML 响应
    RedirectResponse,  # 用于重定向
)
from fastapi.staticfiles import StaticFiles  # 静态文件目录
import config  # 导入配置文件
from typing import Optional
import logging
from db.connection import DatabaseOperation

# 获取日志记录器
logger = logging.getLogger(__name__)

app = FastAPI()  # 创建 FastAPI 实例

db_operation = DatabaseOperation()  # 创建数据库操作对象

# 读取配置文件，获取数据库连接信息
if not os.path.exists(config.private_info_json):
    logger.warning(f"配置文件不存在, 跳过数据库连接，添加重启接口")
else:

    async def startup_event():  # 连接数据库
        await db_operation.connectPool()
        logger.info("连接数据库")

    app.add_event_handler("startup", startup_event)  # 注册事件，项目启动时连接数据库

    async def shutdown_event():  # 关闭数据库连接池
        await db_operation.pool.close()
        logger.info("关闭数据库连接池")

    app.add_event_handler("shutdown", shutdown_event)  # 项目关闭时关闭数据库连接池


app.mount("/static", StaticFiles(directory="static"), name="static")  # 静态文件目录
app.mount("/layui", StaticFiles(directory="layui"), name="layui")  # layui 静态文件目录


@app.get("/favicon.ico")  # 获取网站图标
async def get_favicon():
    return FileResponse("static/favicon.ico", media_type="image/x-icon")  # 返回网站图标


@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/index", status_code=303)


# 指定路由模块的根目录
root_dir = "routes"

# 获取所有 Python 文件的模块路径
for dirpath, _, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith(".py") and filename != "__init__.py":
            # 构建模块路径
            module_path = os.path.join(dirpath, filename)
            module_name = module_path.replace(os.sep, ".")[:-3]  # 去掉 ".py" 扩展名
            module = importlib.import_module(module_name)  # 导入模块
            app.include_router(module.router)  # 注册路由


if __name__ == "__main__":
    logger.info("启动 FastAPI 服务")

    try:
        uvicorn.run(
            app, host=config.host, port=config.port, log_config=None
        )  # 启动 FastAPI 服务
    except KeyboardInterrupt:
        logger.info("关闭 FastAPI 服务")
