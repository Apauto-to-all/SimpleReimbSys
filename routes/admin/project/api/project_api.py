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

from utils import login_utils, user_utils, category_utils, project_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# 创建项目
@router.post("/admin/project/api/create")
async def create_project(
    project_name: str = Form(""),  # 项目名称
    project_source: str = Form(""),  # 项目来源
    category_name: str = Form(""),  # 所属类别
    total_amount: float = Form(0.0),  # 立项金额
    access_token: Optional[str] = Cookie(None),
):
    if (
        not project_name
        or not project_source
        or not category_name
        or not total_amount
        or not access_token
        or total_amount < 0
    ):
        return JSONResponse(content={"message": "参数错误"}, status_code=400)

    user_dict = await user_utils.user_select_all(access_token)
    if user_dict.get("role_name") != "管理员":
        return JSONResponse(content={"message": "无权限"}, status_code=403)

    if not await category_utils.check_category(category_name):
        return JSONResponse(content={"message": "项目类别不存在"}, status_code=400)

    if await project_utils.check_project(project_name):
        return JSONResponse(content={"message": "项目已存在"}, status_code=400)

    if await project_utils.create_project(
        project_name, project_source, category_name, total_amount, total_amount
    ):
        return JSONResponse(content={"message": "创建成功"}, status_code=200)

    return JSONResponse(content={"message": "创建失败"}, status_code=400)
