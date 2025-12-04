# -*- coding: utf-8 -*-
"""
@File    :   documents.py
@Time    :   2025/12/03
@Author  :   pygao
@Version :   2.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文档模型（从 reports.py 重命名）
"""
import enum
import uuid
from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, Enum, func, VARCHAR, JSON, Boolean, Index

from app.database.db import Base


# ==================== 枚举类型 ====================

class DocumentStatus(str, enum.Enum):
    """文档状态"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ChangeType(str, enum.Enum):
    """版本变更类型"""
    AI_GENERATED = "ai_generated"          # AI生成
    MANUAL_EDIT = "manual_edit"            # 用户手动编辑
    CHAPTER_ADDED = "chapter_added"        # 新增章节
    CHAPTER_REWRITTEN = "chapter_rewritten"  # 重写章节
    STATUS_CHANGED = "status_changed"      # 状态变更


# ==================== 文档表 ====================

class Document(Base):
    """文档表（支持交互式生成和版本管理）"""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)  # 用户ID

    # 基本信息
    title = Column(VARCHAR(255), nullable=False, index=True)
    description = Column(Text)

    # Markdown 内容（MinIO图片URL直接嵌入）
    content = Column(Text, nullable=False)

    # 状态
    status = Column(
        Enum(DocumentStatus),
        default=DocumentStatus.DRAFT,
        nullable=False,
        index=True
    )

    # 分类和标签
    category = Column(VARCHAR(50), index=True)
    tags = Column(VARCHAR(500))  # 逗号分隔，如："python,fastapi,demo"

    # ========== 扩展字段 ==========

    # 会话关联
    chat_id = Column(String(36), nullable=True, index=True)  # 关联的会话ID

    # 章节大纲（JSON格式）
    outline = Column(JSON, nullable=True)  # 章节结构和生成状态

    # 版本管理
    current_version = Column(Integer, default=1, nullable=False)  # 当前版本号
    is_manually_edited = Column(Boolean, default=False, nullable=False)  # 是否被手动编辑

    # 统计信息
    word_count = Column(Integer, default=0)  # 字数统计
    estimated_reading_time = Column(Integer, default=0)  # 预计阅读时间（分钟）

    # 时间戳
    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        index=True
    )
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    published_at = Column(TIMESTAMP)

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', version={self.current_version})>"


# ==================== 文档版本历史表 ====================

class DocumentVersion(Base):
    """文档版本历史表 - 记录AI生成和用户编辑的所有版本"""
    __tablename__ = "document_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), nullable=False, index=True)  # 关联的文档ID
    version_number = Column(Integer, nullable=False)  # 版本号（从1开始递增）

    # 版本快照内容
    title = Column(VARCHAR(255), nullable=False)
    content = Column(Text, nullable=False)  # Markdown内容快照
    outline = Column(JSON, nullable=True)  # 章节结构快照

    # 版本元数据
    change_type = Column(
        Enum(ChangeType),
        nullable=False,
        index=True
    )  # 变更类型
    change_summary = Column(Text, nullable=True)  # 变更摘要（用户可填写）
    changed_by = Column(VARCHAR(10), nullable=False)  # "ai" or "user"
    user_id = Column(String(36), nullable=True)  # 编辑用户ID（仅当changed_by="user"时）

    # 时间戳
    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        index=True
    )

    # 复合索引：document_id + version_number 确保查询效率
    __table_args__ = (
        Index('idx_document_version', 'document_id', 'version_number'),
    )

    def __repr__(self):
        return f"<DocumentVersion(document_id={self.document_id}, v={self.version_number}, type={self.change_type})>"


# ==================== 兼容性别名（过渡期使用，后续可移除） ====================
# 为了让依赖 Report/ReportStatus 的代码能平滑过渡
Report = Document
ReportStatus = DocumentStatus
ReportVersion = DocumentVersion
