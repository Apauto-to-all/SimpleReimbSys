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

from utils import account_utils, login_utils, user_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# 创建账户，管理员创建财务人员账户，报销人员账户
@router.post("/admin/user/api/create_account")
async def create_finance_account(
    username: str = Form(""),  # 用户名
    password: str = Form(""),  # 密码
    confirm_password: str = Form(""),  # 确认密码
    real_name: str = Form(""),  # 真实姓名
    role_name: str = Form(""),  # 角色
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
    user_dict = await user_utils.user_select_all(access_token)
    if not user_dict.get("role_name") == "管理员":
        return JSONResponse(content={"message": "没有权限"}, status_code=400)

    # 判断用户名是否存在
    if await user_utils.user_select_all_from_username(username):
        return JSONResponse(content={"message": "用户名已存在"}, status_code=400)

    # 判断密码是否一致
    if password != confirm_password:
        return JSONResponse(content={"message": "两次密码不一致"}, status_code=400)

    # 判断角色是否合法
    if role_name not in ["财务人员", "报销人员"]:
        return JSONResponse(content={"message": "角色不合法"}, status_code=400)

    # 创建账户
    if await account_utils.create_account(username, password, real_name, role_name):
        return JSONResponse(content={"message": "创建账户成功"}, status_code=200)

    return JSONResponse(content={"message": "创建账户失败"}, status_code=400)


# 删除账户
@router.post("/admin/user/api/delete_account")
async def delete_account(
    username: str = Form(""),  # 用户名
    access_token: Optional[str] = Cookie(None),  # 访问令牌
):
    if not username or not access_token:
        return JSONResponse(content={"message": "参数错误"}, status_code=400)

    # 检测是否为管理员
    user_dict = await user_utils.user_select_all(access_token)
    if not user_dict.get("role_name") == "管理员":
        return JSONResponse(content={"message": "没有权限"}, status_code=400)

    # 判断用户名是否存在
    if not await user_utils.user_select_all_from_username(username):
        return JSONResponse(content={"message": "用户名不存在"}, status_code=400)

    # 获取账户信息
    account_dict = await user_utils.user_select_all_from_username(username)
    if account_dict.get("role_name") == "管理员":
        return JSONResponse(content={"message": "不能删除管理员账户"}, status_code=400)

    if account_dict.get("role_name") == "财务人员":
        # 判断财务人员是否分配了项目类别
        if await account_utils.search_user_allocation(username, "财务人员"):
            return JSONResponse(
                content={"message": "该财务人员已分配项目类别，请先删除分配的项目类别"},
                status_code=400,
            )
        # 判断财务人员是否进行了报销审核
        if await account_utils.check_user_reimbursement(username, "财务人员"):
            return JSONResponse(
                content={"message": "该财务人员已进行报销审核，不允许删除！！！"},
                status_code=400,
            )

    if account_dict.get("role_name") == "报销人员":
        if await account_utils.search_user_allocation(username, "报销人员"):
            return JSONResponse(
                content={"message": "该报销人员已分配项目，请先删除分配的项目"},
                status_code=400,
            )
        if await account_utils.check_user_reimbursement(username, "报销人员"):
            return JSONResponse(
                content={"message": "该报销人员已进行报销，不允许删除！！！"},
                status_code=400,
            )

    # 删除账户
    if await account_utils.delete_account(username):
        return JSONResponse(content={"message": "删除账户成功"}, status_code=200)

    return JSONResponse(content={"message": "删除账户失败"}, status_code=400)
