import importlib
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

private_info_path = config.private_info_name + ".py"
if os.path.exists(private_info_path):
    private_info = importlib.import_module(config.private_info_name)
    login_time_minute = private_info.login_time_minute

import logging

from utils import login_utils, password_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/login/api")
async def login(
    username: Optional[str] = Form(""),  # 获取用户名
    password: Optional[str] = Form(""),  # 获取密码
    captcha: Optional[str] = Form(""),  # 获取验证码
    remember: Optional[str] = Form(""),  # 获取记住我
    captcha_token: Optional[str] = Cookie(None),  # 获取验证码的 token
):
    # 检测输入信息是否为空
    if not (username and password and captcha, captcha_token):
        return JSONResponse(
            content={"error": "用户名，密码，验证码不能为空"}, status_code=400
        )
    # 验证码验证
    if not await password_utils.verify_password(captcha_token, captcha.lower()):
        return JSONResponse(content={"error": "验证码错误"}, status_code=400)
    #  验证用户名和密码
    if not await login_utils.verify_login(username, password):
        return JSONResponse(content={"error": "用户名或密码错误"}, status_code=400)
    # 登入成功
    response = RedirectResponse(f"/index", status_code=302)
    if remember == "on":  # 如果勾选了记住我，设置 Cookie 的过期时间
        response.set_cookie(
            key="access_token",  # 设置 Cookie 的键
            value=await password_utils.get_access_jwt(username),  # 设置 Cookie 的值
            max_age=60 * login_time_minute,  # 设置 Cookie 的过期时间
        )
    else:
        response.set_cookie(
            key="access_token",  # 设置 Cookie 的键
            value=await password_utils.get_access_jwt(username),  # 设置 Cookie 的值
        )
    return response
