# -*- coding: utf-8 -*-
"""
@File    :   state.py
@Time    :   2025/11/14 10:14
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""

from operator import add
from app.agents.schemas.document_outline_schema import Section, DocumentOutline
from app.agents.schemas.review_schema import ChapterReviewResult
from typing import TypedDict, Annotated, Dict, Any


class ChapterState(TypedDict):
    """
    Chapter Subgraph 的状态定义（优化版）

    设计原则：
    1. 只保留流程必需的字段
    2. 删除冗余/重复的字段
    3. 统计数据在 Finalizer 中构建，不在 state 中传递
    """
    # ========== 输入（从 Main Graph 传入）==========


    chapter_id: int  # 章节的序号（用于排序）

    document_outline: DocumentOutline  # 整体文章的对象（包含要点、指导等，Writer 需要）

    chapter_outline: Section  # 章节大纲对象（包含要点、指导等，Writer 需要）
    target_word_count: int  # 目标字数（Reviewer 评估长度达标性）

    # ========== Chapter Researcher 输出 ==========
    synthesized_materials: str  # 提炼后的研究素材（Writer 的输入材料）

    # ========== Chapter Writer 输出 ==========
    draft_content: str  # 章节草稿内容（核心输出，Reviewer 输入）
    word_count: int  # 实际字数（Reviewer 评估用，最终统计用）

    # ========== Chapter Reviewer 输出 ==========
    revision_count: int  # 当前修订次数（防止无限修订循环，达到上限强制通过）
    revision_needed: bool  # 是否需要修订（路由决策：True → Writer, False → Finalizer）
    revision_history: Annotated[list[ChapterReviewResult], add]
    review_result: ChapterReviewResult  # 最新的审查结果（Finalizer 需要访问）

    # ========== 返回给父图 ==========
    completed_chapters: Dict[int, Dict[str, Any]]  # 章节完成结果（传递给 DocumentState，key 为 chapter_id）



