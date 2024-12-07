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


# 审核报销api
@router.post("/user/finance/api/audit")
async def audit(
    reimbursement_id: Optional[int] = Form(0),  # 报销ID
    status: Optional[str] = Form(""),  # 审核状态，已通过，已拒绝
    comment: Optional[str] = Form(""),  # 审核意见
    access_token: Optional[str] = Cookie(None),
):
    if not reimbursement_id or not status:
        return JSONResponse(content={"message": "参数不能为空"}, status_code=400)

    if status not in ["已通过", "已拒绝"]:
        return JSONResponse(content={"message": "审核状态错误"}, status_code=400)

    user_dict = await user_utils.user_select_all(access_token)
    if user_dict.get("role_name") != "财务人员":
        return JSONResponse(content={"message": "无权限"}, status_code=403)

    if await reimbursement_utils.check_finance_reimbursement(
        reimbursement_id, user_dict.get("username")
    ):  # 检查是否有权限审核
        return JSONResponse(content={"message": "无权限"}, status_code=403)

    # 进行报销审核
    if await reimbursement_utils.reimbursement_audit(
        reimbursement_id, user_dict.get("username"), status, comment
    ):
        return JSONResponse(content={"message": "审核成功"}, status_code=200)

    return JSONResponse(content={"message": "审核失败"}, status_code=400)
