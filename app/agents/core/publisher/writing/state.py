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
    document_metadata: Dict[str, Any]  # 文档统计信息(字数、章节数、生成耗时等)

    # ========== Document Reviewer 输出 ==========
    latest_review: Any  # 最新审查结果 (ReviewResult)
    revision_count: int  # 修订次数
    document_review: Dict[str, Any]  # 最终审查摘要 (用于输出)


