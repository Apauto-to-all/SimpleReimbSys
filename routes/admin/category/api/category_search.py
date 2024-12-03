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


# 搜索报销(项目)类别api
@router.get("/admin/category/api/search", response_class=JSONResponse)
async def admin_category_search(
    page: int = Query(1),
    limit: int = Query(10),
    category_name: Optional[str] = Query(""),  # 类别名称
    assign: Optional[int] = Query(-1),  # 是否分配，0：未分配，1：已分配，-1：不限
    access_token: Optional[str] = Cookie(None),
):
    user_dict = await user_utils.user_select_all(access_token)
    if user_dict.get("role_name") != "管理员":
        return RedirectResponse("/login", status_code=302)

    count, list_data = await category_utils.search_category_info(
        page, limit, category_name, assign
    )
    return JSONResponse(
        content={"code": 0, "msg": "", "count": count, "data": list_data},
        status_code=200,
    )


# 获取所有报销(项目)类别api
@router.get("/admin/category/api/search_all", response_class=JSONResponse)
async def admin_category_search_all(
    access_token: Optional[str] = Cookie(None),
):
    user_dict = await user_utils.user_select_all(access_token)
    if user_dict.get("role_name") != "管理员":
        return RedirectResponse("/login", status_code=302)

    list_data = await category_utils.search_all_category()
    return JSONResponse(
        content={"data": list_data},
        status_code=200,
    )
