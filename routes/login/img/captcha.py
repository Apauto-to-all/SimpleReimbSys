import importlib
import os
import subprocess
import sys
from fastapi import (
    APIRouter,  # 功能：用于创建路由
    Request,  # 功能：用于接收请求
    Cookie,  # 功能：用于操作 Cookie
    File,  # 功能：用于文件上传
    Form,  # 功能：用于表单提交
    Response,  # 功能：用于返回响应
)
from fastapi.templating import Jinja2Templates  # 功能：用于渲染模板
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import RedirectResponse  # 功能：用于重定向
from typing import Optional  # 功能：用于声明可选参数

# 引入验证码模块
import random
from captcha.image import ImageCaptcha
import string  # 导入 string 模块，用于生成验证码

import config

from utils import password_utils


import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# 获取验证码的图片
@router.get("/login/img/captcha")
async def get_captcha():
    image_captcha = ImageCaptcha()  # 创建图片验证码对象
    captcha_text = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=4)
    )  # 生成随机验证码, 长度为 4，包含大写字母和数字
    data = image_captcha.generate(captcha_text)  # 生成图片验证码
    data.seek(0)  # 移动指针到文件开头
    response = Response(content=data.read(), media_type="image/png")  # 创建响应对象
    captcha_text = captcha_text.lower()  # 将验证码转换为小写
    response.set_cookie(
        key="captcha_token", value=await password_utils.encrypt_password(captcha_text)
    )  # 设置 cookie，存储加密后的验证码
    return response  # 返回图片验证码
