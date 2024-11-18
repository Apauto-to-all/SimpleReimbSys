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

from utils import login_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def init(
    request: Request,
    access_token: Optional[str] = Cookie(None),
):
    if await login_utils.is_login(access_token):
        # 如果已经登入，就重定向到首页
        return RedirectResponse("/index", status_code=302)
    return templates.TemplateResponse("login/login.html", {"request": request})
