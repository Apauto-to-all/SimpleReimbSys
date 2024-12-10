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

from utils import login_utils, user_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/index", response_class=HTMLResponse)
async def index(
    request: Request,
    access_token: Optional[str] = Cookie(None),
):
    # 检测是否登录
    user_dict = await user_utils.user_select_all(access_token)
    if user_dict:
        return templates.TemplateResponse(
            "index.html", {"request": request, "user_dict": user_dict}
        )
    return RedirectResponse("/login", status_code=302)


# about 页面
@router.get("/about", response_class=HTMLResponse)
async def about(
    request: Request,
    access_token: Optional[str] = Cookie(None),
):
    # 检测是否登录
    user_dict = await user_utils.user_select_all(access_token)
    if user_dict:
        return templates.TemplateResponse(
            "about.html", {"request": request, "user_dict": user_dict}
        )

    return RedirectResponse("/login", status_code=302)


# contact 页面
@router.get("/contact", response_class=HTMLResponse)
async def contact(
    request: Request,
    access_token: Optional[str] = Cookie(None),
):
    # 检测是否登录
    user_dict = await user_utils.user_select_all(access_token)
    if user_dict:
        return templates.TemplateResponse(
            "contact.html", {"request": request, "user_dict": user_dict}
        )

    return RedirectResponse("/login", status_code=302)
