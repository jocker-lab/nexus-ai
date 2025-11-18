# -*- coding: utf-8 -*-
"""
@File    :   chapter_finalizer.py
@Time    :   2025/11/14 10:14
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   章节定稿节点 - 格式化章节、收集元数据、保存文档
"""

from typing import Dict, Any
from pathlib import Path
from loguru import logger
from app.agents.core.publisher.subgraphs.chapter_writing.state import ChapterState


async def chapter_finalizer(state: ChapterState) -> Dict[str, Any]:
    """
    章节定稿节点

    职责：
    1. 格式化章节内容
    2. 收集元数据
    3. 提取来源列表
    4. 保存章节文档到文件
    5. 返回给 Main Graph
    """
    chapter_id = state["chapter_id"]

    logger.info(f"[Chapter {chapter_id}] 开始定稿")

    # === 1. 获取最终内容 ===
    final_content = state["draft_content"]

    # === 2. 收集元数据 ===
    chapter_title = state["chapter_outline"].title

    # ✅ 安全获取 review_result
    review_result = state.get("review_result")
    final_score = review_result.overall_score if review_result else 0

    metadata = {
        "chapter_id": chapter_id,
        "chapter_title": chapter_title,
        "word_count": state["word_count"],
        "revision_count": state.get("revision_count", 0),
        "final_score": final_score,
    }

    # === 3. 提取来源 ===
    sources = []

    # === 4. 格式化章节结果 ===
    chapter_result = {
        "chapter_id": chapter_id,
        "final_content": final_content,
        "actual_word_count": state["word_count"],
        "sources": sources,
        "quality_score": metadata["final_score"],
        "revision_count": state.get("revision_count", 0),
        "metadata": metadata,
    }

    # === 6. 打印摘要 ===
    logger.success(
        f"[Chapter {chapter_id}] 定稿完成 - "
        f"字数: {state['word_count']}, "
        f"质量分: {chapter_result['quality_score']}, "
        f"修订次数: {chapter_result['revision_count']}"
    )

    # === 7. 返回给 Main Graph ===
    return_value = {
        "completed_chapters": {
            chapter_id: chapter_result
        }
    }

    # 调试日志
    logger.debug(f"[Chapter {chapter_id}] 返回值类型: {type(return_value)}")
    logger.debug(f"[Chapter {chapter_id}] completed_chapters 键: {list(return_value['completed_chapters'].keys())}")

    return return_value
