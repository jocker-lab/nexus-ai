# -*- coding: utf-8 -*-
"""
@File    :   constants.py
@Time    :   2025/6/4 16:21
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""

class ERROR_MESSAGES:
    ACCESS_PROHIBITED = "Access prohibited"
    NOT_FOUND = "Resource not found"
    DEFAULT = lambda detail="An error occurred": f"Bad request: {detail}"

