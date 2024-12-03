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

from utils import login_utils, user_utils, category_utils, assign_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# 分配财务人员
@router.get("/admin/category/api/assign")
async def admin_category_assign(
    category_name: Optional[str] = Query(""),
    username: Optional[str] = Query(""),
    access_token: Optional[str] = Cookie(None),
):
    if not category_name or not username or not access_token:
        return JSONResponse(content={"message": "参数错误"}, status_code=400)

    user_dict = await user_utils.user_select_all(access_token)
    if user_dict.get("role_name") != "管理员":
        return JSONResponse(content={"message": "无权限"}, status_code=403)

    if not await category_utils.check_category(category_name):
        return JSONResponse(content={"message": "报销类别不存在"}, status_code=400)

    user_dict_account = await user_utils.user_select_all_from_username(username)
    if not user_dict_account:
        return JSONResponse(content={"message": "用户不存在"}, status_code=400)

    if user_dict_account.get("role_name") != "财务人员":
        return JSONResponse(content={"message": "该用户不是财务人员"}, status_code=400)

    # 分配财务人员
    if await assign_utils.assign_category(category_name, username):
        return JSONResponse(content={"message": "分配成功"}, status_code=200)

    return JSONResponse(content={"message": "分配失败"}, status_code=400)
