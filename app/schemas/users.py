# -*- coding: utf-8 -*-
"""
@File    :   users.py
@Time    :   2025/7/2 10:08
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""


from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    profile_image_url: str