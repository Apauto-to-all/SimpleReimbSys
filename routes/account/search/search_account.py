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
    Query,  # 功能：用于查询参数
)
from fastapi.templating import Jinja2Templates  # 功能：用于渲染模板
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Optional  # 功能：用于声明可选参数

import logging

from utils import account_utils, login_utils, role_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/account/search")
async def search_account(
    page: int = Query(1),
    limit: int = Query(10),
    username: Optional[str] = Query(""),  # 用户名
    real_name: Optional[str] = Query(""),  # 真实姓名
    role_name: Optional[str] = Query(""),  # 角色
    access_token: Optional[str] = Cookie(None),
):
    if not await role_utils.is_admin(access_token):
        return RedirectResponse("/login", status_code=302)
    count, list_data = await account_utils.saerch_user_info(
        page, limit, username, real_name, role_name
    )
    return JSONResponse(
        content={"code": 0, "msg": "", "count": count, "data": list_data},
        status_code=200,
    )
