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
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Optional  # 功能：用于声明可选参数

import logging

from utils import account_utils, login_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# 创建账户，管理员创建财务人员账户，报销人员账户
@router.post("/account/api/create_account")
async def create_finance_account(
    username: str = Form(...),  # 用户名
    password: str = Form(...),  # 密码
    confirm_password: str = Form(...),  # 确认密码
    real_name: str = Form(...),  # 真实姓名
    role_name: str = Form(...),  # 角色
    access_token: Optional[str] = Cookie(None),  # 访问令牌
):
    if (
        not username
        or not password
        or not confirm_password
        or not real_name
        or not role_name
    ):
        return JSONResponse(content={"message": "请填写完整信息"}, status_code=400)

    # 检测是否为管理员
    if not await login_utils.is_admin(access_token):
        return JSONResponse(content={"message": "没有权限"}, status_code=400)

    # 判断用户名是否存在
    if account_utils.check_username_exist(username):
        return JSONResponse(content={"message": "用户名已存在"}, status_code=400)

    # 判断密码是否一致
    if password != confirm_password:
        return JSONResponse(content={"message": "两次密码不一致"}, status_code=400)

    # 判断角色是否合法
    if role_name not in ["财务人员", "报销人员"]:
        return JSONResponse(content={"message": "角色不合法"}, status_code=400)

    # 创建账户
    if account_utils.create_account(username, password, real_name, role_name):
        return JSONResponse(content={"message": "创建账户成功"}, status_code=200)

    return JSONResponse(content={"message": "创建账户失败"}, status_code=400)
