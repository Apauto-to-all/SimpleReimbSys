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

from utils import account_utils, login_utils, user_utils, reimbursement_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# 重置密码
@router.post("/user/api/reset_password")
async def reset_password(
    username: str = Form(""),  # 用户名
    password: str = Form(""),  # 密码
    confirm_password: str = Form(""),  # 确认密码
    access_token: Optional[str] = Cookie(None),  # 访问令牌
):
    if not username or not password or not confirm_password:
        return JSONResponse(content={"message": "请填写完整信息"}, status_code=400)

    # 判断密码是否一致
    if password != confirm_password:
        return JSONResponse(content={"message": "两次密码不一致"}, status_code=400)

    # 获取登入用户信息
    user_dict = await user_utils.user_select_all(access_token)
    if not user_dict:
        return JSONResponse(content={"message": "请先登录"}, status_code=400)

    # 判断是否有权限，只有管理员和自己可以重置密码
    if user_dict.get("role_name") != "管理员" and user_dict.get("username") != username:
        return JSONResponse(content={"message": "无权限"}, status_code=400)

    # 无法重置管理员的密码
    user_info = await user_utils.user_select_all_from_username(username)
    if user_info.get("role_name") == "管理员":
        return JSONResponse(
            content={"message": "无法重置管理员的密码"}, status_code=400
        )

    # 重置密码
    if await user_utils.reset_password(username, password):
        return JSONResponse(content={"message": "修改密码成功"}, status_code=200)

    return JSONResponse(content={"message": "修改密码失败"}, status_code=400)


# 获取用户所有可报销的项目名称api
@router.get("/user/api/get_reimbursement_name_list")
async def reimbursement_name(
    access_token: Optional[str] = Cookie(None),
):
    user_dict = await user_utils.user_select_all(access_token)
    if user_dict.get("role_name") == "管理员":
        return JSONResponse(content={"message": "管理员禁止报销"}, status_code=400)

    name_list = await reimbursement_utils.get_reimbursement_name_list(
        user_dict.get("username"), user_dict.get("role_name")
    )

    return JSONResponse(content={"data": name_list}, status_code=200)
