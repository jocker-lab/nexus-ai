# -*- coding: utf-8 -*-
"""
@File    :   document_writing_role.py
@Time    :   2025/11/24 10:43
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""

from pydantic import BaseModel, Field
from typing import List


class TechnicalWriterRole(BaseModel):
    """技术文档专家角色定义"""

    role: str = Field(..., description="角色名称与职位定位。")

    profile: str = Field(..., description="专家背景与能力描述")

    writing_principles: List[str] = Field(..., description="具体可执行的写作规则清单，每条原则需满足SMART原则（具体、可衡量、可操作）。", )

    class Config:
        json_schema_extra = {
            "example": {
                "role": "💻 系统架构与技术文档专家",
                "profile": "你拥有12年软件工程与技术写作双重背景...",
                "writing_principles": [
                    "精准统一地使用技术术语；首次出现时需定义所有缩写",
                ]
            }
        }
