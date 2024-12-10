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


# 报销申请api
@router.post("/user/employee/api/reimbursement_apply")
async def reimbursement_apply(
    project_name: Optional[str] = Form(""),  # 项目名称
    amount: Optional[float] = Form(0.0),  # 报销金额
    description: Optional[str] = Form(""),  # 报销描述
    access_token: Optional[str] = Cookie(None),
):
    if not project_name or not amount or not description:
        return JSONResponse(content={"message": "参数不能为空"}, status_code=400)

    user_dict = await user_utils.user_select_all(access_token)
    if user_dict.get("role_name") != "报销人员":
        return JSONResponse(content={"message": "无权限"}, status_code=403)

    # 进行报销申请
    if await reimbursement_utils.reimbursement_apply(
        project_name, user_dict.get("username"), amount, description
    ):
        return JSONResponse(content={"message": "申请成功"}, status_code=200)

    return JSONResponse(content={"message": "申请失败"}, status_code=400)


# 获取报销人员的报销后的金额
@router.get("/user/employee/api/employee_amount")
async def employee_amount(
    access_token: Optional[str] = Cookie(None),
):
    user_dict = await user_utils.user_select_all(access_token)
    if user_dict.get("role_name") != "报销人员":
        return JSONResponse(content={"message": "无权限"}, status_code=403)

    amount = await reimbursement_utils.get_employee_amount(user_dict.get("username"))
    return JSONResponse(content={"amount": amount}, status_code=200)
