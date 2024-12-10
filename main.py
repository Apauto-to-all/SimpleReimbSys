import importlib
import os
from fastapi import FastAPI, Cookie, Request  # 导入 FastAPI 框架
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
from utils import init_utils

# 获取日志记录器
logger = logging.getLogger(__name__)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)  # 创建 FastAPI 实例

app.mount("/static", StaticFiles(directory="static"), name="static")  # 静态文件目录
app.mount("/layui", StaticFiles(directory="layui"), name="layui")  # layui 静态文件目录


@app.middleware("http")
async def custom_404_redirect(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == 404:
        return RedirectResponse(url="/index")
    return response


db_operation = DatabaseOperation()  # 创建数据库操作对象

# 验证数据库连接信息，如果验证通过，连接数据库，否则跳转到初始化页面
if init_utils.check_private_info():

    async def startup_event():  # 连接数据库
        await db_operation.connectPool()
        logger.info("连接数据库")

    app.add_event_handler("startup", startup_event)  # 注册事件，项目启动时连接数据库

    async def shutdown_event():  # 关闭数据库连接池
        await db_operation.pool.close()
        logger.info("关闭数据库连接池")

    app.add_event_handler("shutdown", shutdown_event)  # 项目关闭时关闭数据库连接池

    # 指定路由模块的根目录
    root_dir = "routes"

    # 获取所有 Python 文件的模块路径
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if (
                filename.endswith(".py")
                and filename != "init.py"
                and filename != "init_api.py"
            ):
                # 构建模块路径
                module_path = os.path.join(dirpath, filename)
                module_name = module_path.replace(os.sep, ".")[:-3]  # 去掉 ".py" 扩展名
                module = importlib.import_module(module_name)  # 导入模块
                app.include_router(module.router)  # 注册路由

    # 添加全局中间件，如果已经初始化，跳转到首页
    @app.middleware("http")
    async def redirect_to_init(request: Request, call_next):
        if request.url.path in ["/init", "/init/api"]:
            return RedirectResponse(url="/index", status_code=303)
        response = await call_next(request)
        return response

else:
    # 注册初始化路由
    from routes.init import init
    from routes.init.api import init_api

    app.include_router(init.router)
    app.include_router(init_api.router)

    # 添加全局中间件，如果没有初始化，跳转到初始化页面
    @app.middleware("http")
    async def redirect_to_init(request: Request, call_next):
        if request.url.path == "/index":
            return RedirectResponse(url="/init")
        response = await call_next(request)
        return response


@app.get("/favicon.ico")  # 获取网站图标
async def get_favicon():
    return FileResponse("static/favicon.ico", media_type="image/x-icon")  # 返回网站图标


@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/index", status_code=303)


if __name__ == "__main__":
    logger.info("启动 FastAPI 服务")

    try:
        uvicorn.run(
            app, host=config.host, port=config.port, log_config=None
        )  # 启动 FastAPI 服务
    except KeyboardInterrupt:
        logger.info("关闭 FastAPI 服务")
