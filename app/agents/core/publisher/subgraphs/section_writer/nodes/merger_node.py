# -*- coding: utf-8 -*-
"""
@File    :   merger_node.py
@Time    :   2025/11/14 10:14
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   章节定稿节点 - 仅添加章节元信息，返回给父图
"""

from typing import Dict, Any
from loguru import logger
from app.agents.core.publisher.subgraphs.section_writer.state import ChapterState


async def chapter_finalizer(state: ChapterState) -> Dict[str, Any]:
    """
    章节定稿节点

    职责：
    1. 收集章节元信息
    2. 格式化返回给父图的数据结构

    注意：本节点仅做数据整理，不做其他操作
    """
    chapter_id = state["chapter_id"]
    chapter_title = state["chapter_outline"].title

    logger.info(f"📦 [Chapter {chapter_id}] 《{chapter_title}》 Finalizer: 开始定稿...")

    # 获取最终草稿内容
    final_content = state.get("draft", "")

    # 获取审查结果
    latest_review = state.get("latest_review")
    final_score = latest_review.score if latest_review else 0
    final_status = latest_review.status if latest_review else "unknown"

    # 收集元信息
    metadata = {
        "chapter_id": chapter_id,
        "chapter_title": chapter_title,
        "word_count": len(final_content),
        "revision_count": state.get("revision_count", 0),
        "final_score": final_score,
        "final_status": final_status,
        "writer_role": state.get("writer_role", ""),
    }

    logger.success(
        f"✅ [Chapter {chapter_id}] 定稿完成 | "
        f"字数: {metadata['word_count']} | "
        f"评分: {final_score} | "
        f"状态: {final_status} | "
        f"修订次数: {metadata['revision_count']}"
    )

    # 返回给父图：包含 content 和 metadata 的结构
    return {
        "completed_chapters": {
            chapter_id: {
                "content": final_content,
                "metadata": metadata,
            }
        },
    }
