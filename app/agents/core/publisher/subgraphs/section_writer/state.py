# -*- coding: utf-8 -*-
"""
@File    :   state.py
@Time    :   2025/11/14 10:14
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   Section Writer Subgraph State

Updated: 2025/11/27
- 移除 research_queries 和 research_data 字段
- 研究和写作由 chapter_content_generation subgraph 处理
"""


from app.agents.schemas.document_outline_schema import Section, DocumentOutline
from app.agents.schemas.review_schema import ReviewResult
from typing import TypedDict, Dict, Any



class ChapterState(TypedDict):
    """
    Chapter Subgraph 的状态定义

    流程:
    1. content_generation 节点调用 chapter_content_generation subgraph
       - 生成搜索查询 + 并行搜索
       - 基于素材写作
       - 素材完整性迭代
       - 输出 draft
    2. reviewer 节点评审 draft
    3. reviser 节点根据反馈修订（循环最多2次）
    4. finalizer 节点输出最终结果
    """
    # ========== 输入（从 Main Graph 传入）==========
    chapter_id: int  # 章节的序号（用于排序）

    writer_role: str
    writer_profile: str
    writing_principles: list[str]

    document_outline: DocumentOutline  # 整体文章的对象（包含要点、指导等）
    chapter_outline: Section  # 章节大纲对象（包含要点、指导等）

    # ========== content_generation 输出 ==========
    # (research_queries 和 research_data 现在在 chapter_content_generation 内部处理)
    draft: str  # 章节草稿内容（核心输出，Reviewer 输入）

    # ========== Chapter Reviewer 输出 ==========
    revision_count: int  # 当前修订次数（防止无限修订循环，达到上限强制通过）
    latest_review: ReviewResult  # 最新的审查结果（Finalizer 需要访问）

    # ========== 返回给父图 ==========
    # 每个章节包含 {"content": str, "metadata": dict}
    completed_chapters: Dict[int, Dict[str, Any]]



