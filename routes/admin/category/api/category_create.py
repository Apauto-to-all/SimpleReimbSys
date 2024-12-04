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

from utils import login_utils, user_utils, category_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# 创建报销(项目)类别api
@router.post("/admin/category/api/create", response_class=JSONResponse)
async def admin_category_create(
    category_name: str = Form(""),
    access_token: Optional[str] = Cookie(None),
):
    if not category_name or not access_token:
        return JSONResponse(content={"message": "参数错误"}, status_code=400)

    user_dict = await user_utils.user_select_all(access_token)
    if user_dict.get("role_name") != "管理员":
        return JSONResponse(content={"message": "无权限"}, status_code=403)

    if await category_utils.check_category(category_name):
        return JSONResponse(content={"message": "类别已存在"}, status_code=400)

    # 创建类别
    if await category_utils.create_category(category_name):
        return JSONResponse(content={"message": "创建成功"}, status_code=200)

    return JSONResponse(content={"message": "创建失败"}, status_code=400)


# 删除项目的api
@router.post("/admin/category/api/delete", response_class=JSONResponse)
async def admin_category_delete(
    category_name: str = Form(""),
    access_token: Optional[str] = Cookie(None),
):
    if not category_name or not access_token:
        return JSONResponse(content={"message": "参数错误"}, status_code=400)

    user_dict = await user_utils.user_select_all(access_token)
    if user_dict.get("role_name") != "管理员":
        return JSONResponse(content={"message": "无权限"}, status_code=403)

    if not await category_utils.check_category(category_name):
        return JSONResponse(content={"message": "类别不存在"}, status_code=400)

    if await category_utils.search_category_projects(category_name):
        return JSONResponse(
            content={"message": "该类别下存在一些项目，请先手动删除这些项目"},
            status_code=400,
        )

    if await category_utils.search_category_assign_users(category_name):
        return JSONResponse(
            content={
                "message": "该项目已被分配给财务人员，请先手动删除该项目下的财务人员"
            },
            status_code=400,
        )

    # 删除类别
    if await category_utils.delete_category(category_name):
        return JSONResponse(content={"message": "删除成功"}, status_code=200)

    return JSONResponse(content={"message": "删除失败"}, status_code=400)
