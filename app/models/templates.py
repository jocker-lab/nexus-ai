# -*- coding: utf-8 -*-
"""
@File    :   templates.py
@Time    :   2025/11/28
@Desc    :   模版表 - 存储用户上传的写作模版
"""

import uuid
from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, VARCHAR, JSON, func

from app.database.db import Base


class Template(Base):
    """模版表"""
    __tablename__ = "templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)  # 上传用户ID

    # ========== 基础信息 ==========
    title = Column(VARCHAR(255), nullable=False, index=True)  # 模版名称
    summary = Column(Text, nullable=False)  # 模版简介（用于向量检索）
    category = Column(VARCHAR(50), index=True)  # 分类

    # ========== 原始内容 ==========
    original_filename = Column(VARCHAR(255))  # 原始文件名
    markdown_content = Column(Text)  # Docling 转换后的 Markdown

    # ========== 风格信息 ==========
    writing_style = Column(VARCHAR(20), default="business")  # 写作风格
    writing_tone = Column(VARCHAR(20), default="neutral")  # 写作语气
    target_audience = Column(Text)  # 目标读者

    # ========== 结构信息 ==========
    sections = Column(JSON)  # 章节结构 JSON
    estimated_total_words = Column(Integer, default=5000)  # 建议总字数
    special_requirements = Column(Text)  # 特殊要求

    # ========== 时间戳 ==========
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

    def __repr__(self):
        return f"<Template(id={self.id}, title='{self.title}', category='{self.category}')>"
