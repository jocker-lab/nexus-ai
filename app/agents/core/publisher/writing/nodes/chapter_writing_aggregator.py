# -*- coding: utf-8 -*-
"""
Aggregator - 收集并验证所有章节结果
"""
from loguru import logger
from typing import Dict, Any
from app.agents.core.publisher.writing.state import DocumentState


def chapter_aggregator(state: DocumentState) -> Dict[str, Any]:
    """
    聚合节点 - 完整性检查 + 统计

    职责：
    1. 验证所有章节完成
    2. 统计汇总信息
    3. 返回 document_metadata

    Args:
        state: DocumentState

    Returns:
        {"document_metadata": {...}}
    """
    logger.info("\n📊 [Aggregator] 收集章节结果...")

    completed = state["completed_chapters"]
    expected_count = len(state["document_outline"].sections)

    # === 1. 完整性检查 ===
    if len(completed) != expected_count:
        missing = set(range(1, expected_count + 1)) - set(completed.keys())
        raise ValueError(f"章节缺失！期望 {expected_count}，实际 {len(completed)}，缺失: {missing}")

    # === 2. 按顺序排序 ===
    sorted_chapters = dict(sorted(completed.items()))

    # === 3. 统计 ===
    # 注意：metadata 中字段名为 final_score（来自 merger_node）
    total_words = sum(ch["metadata"]["word_count"] for ch in sorted_chapters.values())
    avg_score = sum(ch["metadata"]["final_score"] for ch in sorted_chapters.values()) / expected_count

    logger.info(f"  ✓ 完整性通过：{len(completed)}/{expected_count} 章节")
    logger.info(f"  ✓ 总字数: {total_words}")
    logger.info(f"  ✓ 平均评分: {avg_score:.1f}\n")

    return {
        "document_metadata": {
            "total_chapters": expected_count,
            "total_words": total_words,
            "avg_score": round(avg_score, 2),
        }
    }
