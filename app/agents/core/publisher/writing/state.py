# -*- coding: utf-8 -*-
"""
@File    :   state.py
@Time    :   2025/11/14 10:39
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
from typing import TypedDict, Dict, Any, Annotated

from app.agents.schemas.document_outline_schema import DocumentOutline

"""
Document State - Main Graph 的状态定义
"""
from operator import or_
from typing import TypedDict, Dict, Any, Annotated
from app.agents.schemas.document_outline_schema import DocumentOutline


class DocumentState(TypedDict):
    """Main Graph 的状态"""
    chat_id: str  # uuid
    document_id: str  # uuid

    writer_role: str
    writer_profile: str
    writing_principles: list[str]

    # ========== Outline Parser 输出 ==========
    document_outline: DocumentOutline  # 主文档大纲

    # ========== Chapter Dispatcher 输出 ==========
    # 每个章节包含 {"content": str, "metadata": dict}
    completed_chapters: Annotated[Dict[int, Dict[str, Any]], or_]

    # ========== Document Integrator 输出 ==========
    document: str  # 整合后的完整文档内容

    # ========== Document Finalizer 输出 ==========
    # 文档元数据（由 LLM with_structured_output 提取）
    # 包含: title, description, category, tags, word_count,
    #       estimated_reading_time, key_insights, target_audience, status
    document_metadata: Dict[str, Any]


