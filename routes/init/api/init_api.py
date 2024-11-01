import os
import subprocess
import sys
import config
from fastapi import (
    APIRouter,  # 功能：用于创建路由
    Request,  # 功能：用于接收请求
    Cookie,  # 功能：用于操作 Cookie
    File,  # 功能：用于文件上传
    Form,  # 功能：用于表单提交
)
from fastapi.templating import Jinja2Templates  # 功能：用于渲染模板
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import RedirectResponse  # 功能：用于重定向
from typing import Optional  # 功能：用于声明可选参数

import logging

from utils import init_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/init/api")
async def init(
    pgsql_host: str = Form(...),
    pgsql_port: int = Form(...),
    pgsql_user: str = Form(...),
    pgsql_password: str = Form(...),
    database_name: str = Form(...),
):
    if (
        not pgsql_host
        or not pgsql_port
        or not pgsql_user
        or not pgsql_password
        or not database_name
    ):
        return JSONResponse(content={"error": "请填写完整信息"}, status_code=400)
    # 尝试连接数据库，创建表，写入数据库连接信息到配置文件
    if await init_utils.is_connectable(
        pgsql_host, pgsql_port, pgsql_user, pgsql_password, database_name
    ):
        # 重启 FastAPI 应用程序
        try:
            # 重新启动当前的 Python 进程
            subprocess.Popen([sys.executable] + sys.argv)
            os._exit(0)
        except Exception as e:
            return {"error": str(e)}
    return JSONResponse(content={"error": "提供连接信息不正确"}, status_code=400)
