# -*- coding: utf-8 -*-
"""
@File    :   writing_templates.py
@Time    :   2025/12/03
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   写作模版模型
"""
import enum
import uuid
from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, Enum, func, VARCHAR, JSON, Index, ForeignKey
from sqlalchemy.dialects.mysql import MEDIUMTEXT

from app.database.db import Base


# ==================== 枚举类型 ====================

class WritingStyle(str, enum.Enum):
    """写作风格"""
    ACADEMIC = "academic"          # 学术
    BUSINESS = "business"          # 商务
    TECHNICAL = "technical"        # 技术
    CREATIVE = "creative"          # 创意
    JOURNALISTIC = "journalistic"  # 新闻


class WritingTone(str, enum.Enum):
    """写作语气"""
    FORMAL = "formal"              # 正式
    NEUTRAL = "neutral"            # 中性
    CASUAL = "casual"              # 随意
    PROFESSIONAL = "professional"  # 专业
    PERSUASIVE = "persuasive"      # 说服性


class TemplateStatus(str, enum.Enum):
    """模版解析状态"""
    PENDING = "pending"            # 待解析
    PARSING = "parsing"            # 解析中
    COMPLETED = "completed"        # 解析完成
    FAILED = "failed"              # 解析失败


class TemplateScope(str, enum.Enum):
    """模版作用域"""
    PRIVATE = "private"            # 仅创建者可见
    SHARED = "shared"              # 可分享给特定用户
    PUBLIC = "public"              # 公开模版


# ==================== 写作模版表 ====================

class WritingTemplate(Base):
    """写作模版表"""
    __tablename__ = "writing_templates"

    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 基础信息
    title = Column(VARCHAR(255), nullable=False, comment="模版标题")
    summary = Column(Text, nullable=False, comment="模版摘要/描述")
    category = Column(VARCHAR(50), comment="分类")

    # 来源信息
    original_filename = Column(VARCHAR(255), comment="原始文件名（如从文档解析）")
    markdown_content = Column(MEDIUMTEXT, comment="完整 Markdown 内容")

    # 写作参数
    writing_style = Column(
        Enum(WritingStyle, values_callable=lambda x: [e.value for e in x]),
        default=WritingStyle.BUSINESS,
        comment="写作风格"
    )
    writing_tone = Column(
        Enum(WritingTone, values_callable=lambda x: [e.value for e in x]),
        default=WritingTone.NEUTRAL,
        comment="写作语气"
    )
    target_audience = Column(Text, comment="目标受众描述")

    # 结构化内容
    sections = Column(JSON, comment="章节结构定义")

    # 解析状态
    status = Column(
        Enum(TemplateStatus, values_callable=lambda x: [e.value for e in x]),
        default=TemplateStatus.PENDING,
        comment="解析状态"
    )
    error_message = Column(Text, comment="解析失败时的错误信息")

    # 作用域
    scope = Column(
        Enum(TemplateScope, values_callable=lambda x: [e.value for e in x]),
        default=TemplateScope.PRIVATE,
        comment="可见范围"
    )

    # 使用统计
    usage_count = Column(Integer, default=0, comment="使用次数")

    # 关联
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False, index=True, comment="创建者")

    # 时间戳
    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="创建时间"
    )
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    # 复合索引优化查询
    __table_args__ = (
        Index('ix_wt_user_status', 'user_id', 'status'),
        Index('ix_wt_user_category', 'user_id', 'category'),
        Index('ix_wt_scope_status', 'scope', 'status'),
        {'comment': '写作模版表'}
    )

    def __repr__(self):
        return f"<WritingTemplate(id={self.id}, title='{self.title}', status={self.status})>"
