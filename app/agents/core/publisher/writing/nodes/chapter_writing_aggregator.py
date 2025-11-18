"""
Aggregator - 收集并验证所有章节结果
"""
from loguru import logger
from typing import Dict, Any
from app.agents.core.publisher.writing.state import DocumentState
from app.agents.core.publisher.writing import config

def chapter_aggregator(state: DocumentState) -> Dict[str, Any]:
    """
    聚合节点
    
    职责：
    1. 等待所有 Subgraph 完成（LangGraph 自动处理）
    2. 验证完整性
    3. 质量统计
    4. 异常检测
    
    Args:
        state: DocumentState
        
    Returns:
        更新后的 state 字段
    """
    logger.info("\n📊 [Aggregator] 收集章节结果...")

    # 调试日志
    logger.debug(f"  🔍 [DEBUG] State 类型: {type(state)}")
    logger.debug(f"  🔍 [DEBUG] State 键: {list(state.keys())}")
    logger.debug(f"  🔍 [DEBUG] completed_chapters 键存在: {'completed_chapters' in state}")

    completed = state["completed_chapters"]

    logger.debug(f"  🔍 [DEBUG] completed_chapters 类型: {type(completed)}")
    logger.debug(f"  🔍 [DEBUG] completed_chapters 值: {completed}")
    logger.debug(f"  🔍 [DEBUG] completed_chapters 长度: {len(completed)}")

    expected_count = len(state["main_document_outline"].sections)
    
    # === 1. 完整性检查 ===
    if len(completed) != expected_count:
        missing_ids = set(range(1, expected_count + 1)) - set(completed.keys())
        
        error_msg = (
            f"章节缺失！期望 {expected_count} 章，实际完成 {len(completed)} 章。"
            f"缺失章节ID: {missing_ids}"
        )
        logger.error(f"  ❌ {error_msg}")
        raise ValueError(error_msg)

    logger.info(f"  ✓ 完整性检查通过：{len(completed)}/{expected_count} 章节")
    
    # === 2. 按顺序排序 ===
    sorted_chapters = dict(sorted(completed.items()))
    
    # === 3. 质量统计 ===
    total_words = sum(ch["actual_word_count"] for ch in sorted_chapters.values())
    avg_score = sum(ch["quality_score"] for ch in sorted_chapters.values()) / expected_count
    
    revision_stats = {
        ch_id: ch["revision_count"]
        for ch_id, ch in sorted_chapters.items()
    }
    
    low_quality_chapters = [
        ch_id for ch_id, ch in sorted_chapters.items()
        if ch["quality_score"] < config.MIN_QUALITY_SCORE
    ]
    
    quality_stats = {
        "total_words": total_words,
        "avg_score": round(avg_score, 2),
        "revision_stats": revision_stats,
        "low_quality_chapters": low_quality_chapters,
    }
    
    logger.info(f"  ✓ 总字数: {total_words}")
    logger.info(f"  ✓ 平均质量分: {avg_score:.1f}")
    logger.info(f"  ✓ 修订统计: {revision_stats}")

    # === 4. 异常检测和日志记录 ===
    warnings_count = 0

    # 检查1：是否有低质量章节
    if low_quality_chapters:
        logger.warning(f"  ⚠️  发现低质量章节: {low_quality_chapters} (低于 {config.MIN_QUALITY_SCORE} 分)")
        warnings_count += 1

    # 检查2：字数分布是否合理
    word_counts = [ch["actual_word_count"] for ch in sorted_chapters.values()]
    if max(word_counts) > 2 * min(word_counts):
        logger.warning(f"  ⚠️  章节长度不平衡: 最长 {max(word_counts)} 字, 最短 {min(word_counts)} 字")
        warnings_count += 1

    if warnings_count == 0:
        logger.info(f"  ✓ 未发现异常\n")
    else:
        logger.warning(f"  ⚠️  发现 {warnings_count} 个警告\n")
    
    # === 返回更新 ===
    # aggregator 负责统计和验证
    # - completed_chapters 已通过 reducer 自动合并,不应重复返回
    # - 警告信息通过日志记录，不需要存储在 state 中
    return {
        "quality_stats": quality_stats,
    }
