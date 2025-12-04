# -*- coding: utf-8 -*-
"""
@File    :   documents.py
@Time    :   2025/12/03
@Author  :   pygao
@Version :   2.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文档相关Pydantic Schema（从 reports.py 重命名）
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


# ==================== 文档相关 Schema ====================

class DocumentCreate(BaseModel):
    """创建文档请求"""
    title: str = Field(..., min_length=1, max_length=255, description="文档标题")
    description: Optional[str] = Field(None, description="文档描述")
    content: str = Field(default="", description="Markdown内容")
    chat_id: Optional[str] = Field(None, description="关联会话ID")
    outline: Optional[Dict[str, Any]] = Field(None, description="章节大纲JSON")
    category: Optional[str] = Field(None, max_length=50, description="分类")
    tags: Optional[str] = Field(None, max_length=500, description="标签（逗号分隔）")
    status: Optional[str] = Field(default="draft", description="状态: draft/published/archived")


class DocumentUpdate(BaseModel):
    """更新文档请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    outline: Optional[Dict[str, Any]] = None
    category: Optional[str] = Field(None, max_length=50)
    tags: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None
    change_summary: Optional[str] = Field(None, description="变更摘要")


class DocumentResponse(BaseModel):
    """文档响应（完整版）"""
    id: str
    user_id: str
    title: str
    description: Optional[str]
    content: str
    status: str
    category: Optional[str]
    tags: Optional[str]

    # 扩展字段
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


class DocumentListItem(BaseModel):
    """文档列表项（简化版，用于列表显示）"""
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

class DocumentVersionResponse(BaseModel):
    """版本历史响应"""
    id: str
    document_id: str
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


class DocumentVersionDetail(BaseModel):
    """版本详细信息（包含完整内容）"""
    id: str
    document_id: str
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


# ==================== 会话文档关联 Schema ====================

class DocumentSessionCreate(BaseModel):
    """创建文档生成会话请求"""
    topic: str = Field(..., min_length=1, description="研究主题")
    research_depth: Optional[str] = Field(default="medium", description="研究深度: quick/medium/deep")
    target_audience: Optional[str] = Field(None, description="目标读者")
    category: Optional[str] = None
    tags: Optional[str] = None


class DocumentSessionResponse(BaseModel):
    """文档生成会话响应"""
    chat_id: str
    document_id: str
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


# ==================== 兼容性别名（过渡期使用，后续可移除） ====================
ReportCreate = DocumentCreate
ReportUpdate = DocumentUpdate
ReportResponse = DocumentResponse
ReportListItem = DocumentListItem
ReportVersionResponse = DocumentVersionResponse
ReportVersionDetail = DocumentVersionDetail
ReportSessionCreate = DocumentSessionCreate
ReportSessionResponse = DocumentSessionResponse
