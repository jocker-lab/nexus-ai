# -*- coding: utf-8 -*-
"""
@File    :   reports.py
@Time    :   2025/10/10 10:33
@Author  :   pygao
@Version :   1.0 (Extended for version management)
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   报告相关Pydantic Schema - 支持版本管理
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


# ==================== 报告相关 Schema ====================

class ReportCreate(BaseModel):
    """创建报告请求"""
    title: str = Field(..., min_length=1, max_length=255, description="报告标题")
    description: Optional[str] = Field(None, description="报告描述")
    content: str = Field(default="", description="Markdown内容")
    chat_id: Optional[str] = Field(None, description="关联会话ID")
    outline: Optional[Dict[str, Any]] = Field(None, description="章节大纲JSON")
    category: Optional[str] = Field(None, max_length=50, description="分类")
    tags: Optional[str] = Field(None, max_length=500, description="标签（逗号分隔）")
    status: Optional[str] = Field(default="draft", description="状态: draft/published/archived")


class ReportUpdate(BaseModel):
    """更新报告请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    outline: Optional[Dict[str, Any]] = None
    category: Optional[str] = Field(None, max_length=50)
    tags: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None
    change_summary: Optional[str] = Field(None, description="变更摘要")


class ReportResponse(BaseModel):
    """报告响应（完整版）"""
    id: str
    user_id: str
    title: str
    description: Optional[str]
    content: str
    status: str
    category: Optional[str]
    tags: Optional[str]

    # 新增字段
    chat_id: Optional[str]
    outline: Optional[Dict[str, Any]]
    current_version: int
    is_manually_edited: bool
    word_count: int
    estimated_reading_time: int

    # 时间戳
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReportListItem(BaseModel):
    """报告列表项（简化版，用于列表显示）"""
    id: str
    title: str
    description: Optional[str]
    status: str
    category: Optional[str]
    current_version: int
    word_count: int
    is_manually_edited: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 版本相关 Schema ====================

class ReportVersionResponse(BaseModel):
    """版本历史响应"""
    id: str
    report_id: str
    version_number: int

    # 版本快照（简化版，不返回完整content）
    title: str
    outline: Optional[Dict[str, Any]]

    # 版本元数据
    change_type: str  # ai_generated, manual_edit, chapter_added, etc.
    change_summary: Optional[str]
    changed_by: str  # "ai" or "user"
    user_id: Optional[str]

    created_at: datetime

    class Config:
        from_attributes = True


class ReportVersionDetail(BaseModel):
    """版本详细信息（包含完整内容）"""
    id: str
    report_id: str
    version_number: int

    # 完整快照
    title: str
    content: str  # 完整Markdown内容
    outline: Optional[Dict[str, Any]]

    # 元数据
    change_type: str
    change_summary: Optional[str]
    changed_by: str
    user_id: Optional[str]

    created_at: datetime

    class Config:
        from_attributes = True


class VersionRollbackRequest(BaseModel):
    """版本回滚请求"""
    version_number: int = Field(..., ge=1, description="要回滚到的版本号")


# ==================== 会话报告关联 Schema ====================

class ReportSessionCreate(BaseModel):
    """创建报告生成会话请求"""
    topic: str = Field(..., min_length=1, description="研究主题")
    research_depth: Optional[str] = Field(default="medium", description="研究深度: quick/medium/deep")
    target_audience: Optional[str] = Field(None, description="目标读者")
    category: Optional[str] = None
    tags: Optional[str] = None


class ReportSessionResponse(BaseModel):
    """报告生成会话响应"""
    chat_id: str
    report_id: str
    blueprint_thread_id: str
    topic: str

    class Config:
        from_attributes = True


# ==================== 章节大纲相关 Schema ====================

class ChapterInfo(BaseModel):
    """章节信息"""
    id: str
    order: int
    title: str
    status: str  # planning, researching, writing, completed
    word_count: int
    subsections: Optional[List[str]] = None
    generated_at: Optional[int] = None
    last_updated: Optional[int] = None


class OutlineResponse(BaseModel):
    """大纲响应"""
    total_chapters: int
    current_chapter: int
    chapters: List[ChapterInfo]
    generation_meta: Optional[Dict[str, Any]] = None


class OutlineUpdateRequest(BaseModel):
    """更新大纲请求"""
    outline: Dict[str, Any] = Field(..., description="完整的大纲JSON结构")