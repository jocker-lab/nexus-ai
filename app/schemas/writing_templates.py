# -*- coding: utf-8 -*-
"""
@File    :   writing_templates.py
@Time    :   2025/12/03
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   写作模版相关 Pydantic Schema
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# ==================== 枚举类型 ====================

class WritingStyleEnum(str, Enum):
    """写作风格"""
    ACADEMIC = "academic"
    BUSINESS = "business"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    JOURNALISTIC = "journalistic"


class WritingToneEnum(str, Enum):
    """写作语气"""
    FORMAL = "formal"
    NEUTRAL = "neutral"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    PERSUASIVE = "persuasive"


class TemplateStatusEnum(str, Enum):
    """模版解析状态"""
    PENDING = "pending"
    PARSING = "parsing"
    COMPLETED = "completed"
    FAILED = "failed"


class TemplateScopeEnum(str, Enum):
    """模版作用域"""
    PRIVATE = "private"
    SHARED = "shared"
    PUBLIC = "public"


# ==================== 章节结构 Schema ====================

class SectionSchema(BaseModel):
    """章节结构"""
    section_number: str = Field(..., description="章节编号，如 '1', '1.1'")
    title: str = Field(..., description="章节标题")
    writing_guidance: Optional[str] = Field(None, description="写作指导")
    estimated_words: Optional[int] = Field(None, description="预计字数")
    subsections: Optional[List['SectionSchema']] = Field(None, description="子章节")


# ==================== 写作模版 Schema ====================

class WritingTemplateCreate(BaseModel):
    """创建写作模版请求"""
    title: str = Field(..., min_length=1, max_length=255, description="模版标题")
    summary: str = Field(..., min_length=1, description="模版摘要/描述")
    category: Optional[str] = Field(None, max_length=50, description="分类")

    # 来源信息
    original_filename: Optional[str] = Field(None, max_length=255, description="原始文件名")
    markdown_content: Optional[str] = Field(None, description="完整 Markdown 内容")

    # 写作参数
    writing_style: Optional[WritingStyleEnum] = Field(
        default=WritingStyleEnum.BUSINESS,
        description="写作风格"
    )
    writing_tone: Optional[WritingToneEnum] = Field(
        default=WritingToneEnum.NEUTRAL,
        description="写作语气"
    )
    target_audience: Optional[str] = Field(None, description="目标受众描述")

    # 结构化内容
    sections: Optional[List[Dict[str, Any]]] = Field(None, description="章节结构定义")

    # 作用域
    scope: Optional[TemplateScopeEnum] = Field(
        default=TemplateScopeEnum.PRIVATE,
        description="可见范围"
    )


class WritingTemplateUpdate(BaseModel):
    """更新写作模版请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="模版标题")
    summary: Optional[str] = Field(None, description="模版摘要/描述")
    category: Optional[str] = Field(None, max_length=50, description="分类")

    # 来源信息
    markdown_content: Optional[str] = Field(None, description="完整 Markdown 内容")

    # 写作参数
    writing_style: Optional[WritingStyleEnum] = Field(None, description="写作风格")
    writing_tone: Optional[WritingToneEnum] = Field(None, description="写作语气")
    target_audience: Optional[str] = Field(None, description="目标受众描述")

    # 结构化内容
    sections: Optional[List[Dict[str, Any]]] = Field(None, description="章节结构定义")

    # 状态
    status: Optional[TemplateStatusEnum] = Field(None, description="解析状态")
    error_message: Optional[str] = Field(None, description="错误信息")

    # 作用域
    scope: Optional[TemplateScopeEnum] = Field(None, description="可见范围")


class WritingTemplateResponse(BaseModel):
    """写作模版响应（完整版）"""
    id: str
    user_id: str

    # 基础信息
    title: str
    summary: str
    category: Optional[str]

    # 来源信息
    original_filename: Optional[str]
    markdown_content: Optional[str]

    # 写作参数
    writing_style: str
    writing_tone: str
    target_audience: Optional[str]

    # 结构化内容
    sections: Optional[List[Dict[str, Any]]]

    # 状态
    status: str
    error_message: Optional[str]

    # 作用域
    scope: str

    # 统计
    usage_count: int

    # 时间戳
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WritingTemplateListItem(BaseModel):
    """写作模版列表项（简化版，用于列表显示）"""
    id: str
    title: str
    summary: str
    category: Optional[str]
    writing_style: str
    writing_tone: str
    status: str
    scope: str
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WritingTemplateListResponse(BaseModel):
    """写作模版列表响应"""
    items: List[WritingTemplateListItem]
    total: int
    page: int
    page_size: int


# ==================== 使用模版相关 Schema ====================

class UseTemplateRequest(BaseModel):
    """使用模版请求"""
    template_id: str = Field(..., description="模版ID")


class UseTemplateResponse(BaseModel):
    """使用模版响应"""
    template_id: str
    usage_count: int
    message: str = "模版使用成功"
