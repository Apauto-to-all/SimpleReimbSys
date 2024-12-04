from itertools import count
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

from utils import login_utils, user_utils, category_utils, project_utils, assign_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/admin/project/api/assign")
async def admin_project_assign(
    project_name: Optional[str] = Form(""),
    usernames: Optional[list] = Form([]),
    access_token: Optional[str] = Cookie(None),
):
    if not project_name or not usernames or not access_token:
        return JSONResponse(content={"message": "参数错误"}, status_code=400)

    user_dict = await user_utils.user_select_all(access_token)
    if user_dict.get("role_name") != "管理员":
        return JSONResponse(content={"message": "无权限"}, status_code=403)

    # 校验项目是否存在
    if not await project_utils.check_project(project_name):
        return JSONResponse(content={"message": "项目不存在"}, status_code=400)

    # 校验并过滤有效的报销人员
    valid_user_names = []
    for username in usernames:
        user_info = await user_utils.user_select_all_from_username(username)
        if user_info and user_info.get("role_name") == "报销人员":
            valid_user_names.append(username)

    if not valid_user_names:
        return JSONResponse(
            content={"message": "未找到有效的报销人员"}, status_code=400
        )

    # 分配报销人员
    if await assign_utils.assign_project(project_name, valid_user_names):
        return JSONResponse(content={"message": "分配成功"}, status_code=200)

    return JSONResponse(content={"message": "分配失败"}, status_code=400)


# 删除项目的分配人员
@router.post("/admin/project/api/unassign")
async def admin_project_unassign(
    project_name: Optional[str] = Form(""),
    usernames: Optional[list] = Form([]),
    access_token: Optional[str] = Cookie(None),
):
    if not project_name or not usernames or not access_token:
        return JSONResponse(content={"message": "参数错误"}, status_code=400)

    user_dict = await user_utils.user_select_all(access_token)
    if user_dict.get("role_name") != "管理员":
        return JSONResponse(content={"message": "无权限"}, status_code=403)

    # 校验项目是否存在
    if not await project_utils.check_project(project_name):
        return JSONResponse(content={"message": "项目不存在"}, status_code=400)

    # 校验并过滤有效的报销人员
    valid_user_names = []
    for username in usernames:
        user_info = await user_utils.user_select_all_from_username(username)
        if user_info and user_info.get("role_name") == "报销人员":
            valid_user_names.append(username)

    if not valid_user_names:
        return JSONResponse(
            content={"message": "未找到有效的报销人员"}, status_code=400
        )

    # 删除报销人员
    if await assign_utils.unassign_project(project_name, valid_user_names):
        return JSONResponse(content={"message": "删除成功"}, status_code=200)

    return JSONResponse(content={"message": "删除失败"}, status_code=400)
