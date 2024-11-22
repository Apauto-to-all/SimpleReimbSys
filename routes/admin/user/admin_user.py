from fastapi import (
    APIRouter,  # 功能：用于创建路由
    Request,
    Cookie,  # 功能：用于操作 Cookie
    File,  # 功能：用于文件上传
)
from fastapi.templating import Jinja2Templates  # 功能：用于渲染模板
from fastapi.responses import HTMLResponse, JSONResponse  # 功能：用于返回 HTML 响应
from fastapi.responses import RedirectResponse  # 功能：用于重定向
from typing import Optional  # 功能：用于声明可选参数

import logging  # 功能：用于记录日志

from utils import login_utils, role_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# 用户管理页面
@router.get("/admin/user", response_class=HTMLResponse)
async def admin_user(
    request: Request,
    access_token: Optional[str] = Cookie(None),
):
    if await role_utils.is_admin(access_token):
        return templates.TemplateResponse(
            "admin/admin_user.html",
            {"request": request, "role_name": "管理员"},
        )
    return RedirectResponse("/index", status_code=302)
