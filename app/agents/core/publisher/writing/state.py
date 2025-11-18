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
from typing import TypedDict, Dict, List, Any, Annotated
from app.agents.schemas.document_outline_schema import DocumentOutline

class ChapterConfig(TypedDict):
    """章节配置

    注意: 使用 writing_config 而不是 style_guide
    避免与 DocumentState.style_guide 同名导致并发冲突
    """
    chapter_id: int
    chapter_title: str
    chapter_outline: List[str]  # 本章要点
    target_word_count: int
    writing_config: Dict[str, Any]  # 包含 global_context, shared_glossary 等
    writing_priority: str  # 写作优先级

class ChapterResult(TypedDict):
    """章节结果"""
    chapter_id: int
    final_content: str
    actual_word_count: int
    sources: List[str]
    quality_score: int
    revision_count: int
    metadata: Dict[str, Any]


def merge_chapter_results(
        existing: Dict[int, ChapterResult],
        new: Dict[int, ChapterResult]
) -> Dict[int, ChapterResult]:
    """
    Reducer 函数：合并章节结果

    这个函数会被 LangGraph 自动调用，用于合并多个 Subgraph 的返回值
    """
    merged = dict(existing)
    merged.update(new)
    return merged


class DocumentState(TypedDict):
    """Main Graph 的状态"""
    chat_id: str # uuid
    document_id: str # uuid

    # ========== Outline Parser 输出 ==========
    # ✅ 修复：使用不同的字段名，避免与 ChapterState.document_outline 冲突
    main_document_outline: DocumentOutline # 主文档大纲（避免与 subgraph 冲突）
    global_context: str  # 全局背景
    global_glossary: Dict[str, str]  # 全局术语表
    chapter_configs: List[ChapterConfig]  # 章节配置列表
    target_length: int  # 目标文档总字数

    # ========== Chapter Dispatcher 输出 ==========
    # 注意：这里使用 Annotated + Reducer 实现自动合并
    completed_chapters: Annotated[
        Dict[int, ChapterResult],
        merge_chapter_results  # 指定 Reducer 函数
    ]

    # ========== Aggregator 输出 ==========
    quality_stats: Dict[str, Any]  # 质量统计
    warnings: List[Dict[str, Any]]  # 警告信息

    # ========== Document Integrator 输出 ==========
    integrated_document: str  # 整合后的文档
    document_metadata: Dict[str, Any]  # 文档元数据

    # ========== Global Reviewer 输出 ==========
    global_review: Dict[str, Any]  # 全局审查结果
    final_document: str  # 最终文档

    # ========== 元数据 ==========
    generation_time: float  # 生成耗时（秒）
