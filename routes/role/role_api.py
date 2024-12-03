from fastapi import (
    APIRouter,  # 功能：用于创建路由
    Request,  # 功能：用于接收请求
    Cookie,  # 功能：用于操作 Cookie
    File,  # 功能：用于文件上传
    Form,  # 功能：用于表单提交
    Query,  # 功能：用于查询参数
)
from fastapi.templating import Jinja2Templates  # 功能：用于渲染模板
from fastapi.responses import HTMLResponse, JSONResponse  # 功能：用于返回 HTML 响应
from fastapi.responses import RedirectResponse  # 功能：用于重定向
from typing import Optional  # 功能：用于声明可选参数

import logging  # 功能：用于记录日志

from utils import login_utils, user_utils, role_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# 获取角色列表api
@router.get("/role/api/search_all")
async def search_all_category(
    access_token: Optional[str] = Cookie(None),
):
    user_dict = await user_utils.user_select_all(access_token)
    if user_dict.get("role_name") != "管理员":
        return RedirectResponse("/login", status_code=302)

    list_data = await role_utils.get_all_role()
    return JSONResponse(
        content={"data": list_data},
        status_code=200,
    )
