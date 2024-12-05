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

from utils import login_utils, user_utils, reimbursement_utils

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# 搜索报销细明api
@router.get("/reimbursement/api/search", response_class=JSONResponse)
async def reimbursement_search(
    page: int = Query(1),
    limit: int = Query(10),
    employee_username: Optional[str] = Query(""),  # 报销人员用户名
    employee_real_name: Optional[str] = Query(""),  # 报销人员真实姓名
    finance_username: Optional[str] = Query(""),  # 财务人员用户名
    finance_real_name: Optional[str] = Query(""),  # 财务人员真实姓名
    category_name: Optional[str] = Query(""),  # 类别名称
    project_name: Optional[str] = Query(""),  # 项目名称
    status: Optional[str] = Query(""),  # 报销状态，待审核，已审核，已拒绝
    access_token: Optional[str] = Cookie(None),
):
    user_dict = await user_utils.user_select_all(access_token)
    if not user_dict:
        return RedirectResponse("/login", status_code=302)

    role_name = user_dict.get("role_name")
    count, list_data = await reimbursement_utils.search_reimbursement_info(
        page,
        limit,
        user_dict.get("username"),
        employee_username,
        employee_real_name,
        finance_username,
        finance_real_name,
        category_name,
        project_name,
        status,
        role_name,
    )

    return JSONResponse(
        content={"code": 0, "msg": "", "count": count, "data": list_data},
        status_code=200,
    )
