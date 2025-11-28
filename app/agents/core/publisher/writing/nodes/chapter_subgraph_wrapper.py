# -*- coding: utf-8 -*-
"""
@File    :   chapter_subgraph_wrapper.py
@Time    :   2025/11/25
@Desc    :   Chapter Subgraph Wrapper - 包装节点实现 State 隔离

解决问题：
    当使用 Send API 并发执行多个 chapter_subgraph 时，
    如果直接将 compiled subgraph 作为节点，LangGraph 会尝试将 subgraph 的完整输出 state
    合并回父图，导致 writer_role 等字段收到多个值，触发 INVALID_CONCURRENT_GRAPH_UPDATE 错误。

解决方案：
    使用包装函数节点，手动调用 subgraph.ainvoke()，只返回需要合并的字段（completed_chapters），
    实现 state 隔离。
"""
from typing import Dict, Any
from loguru import logger
from app.agents.core.publisher.subgraphs.section_writer.agent import create_chapter_subgraph

# 在模块级别创建 subgraph 实例（避免重复编译）
_chapter_subgraph = None


def get_chapter_subgraph():
    """懒加载 subgraph 实例"""
    global _chapter_subgraph
    if _chapter_subgraph is None:
        _chapter_subgraph = create_chapter_subgraph()
    return _chapter_subgraph


async def chapter_subgraph_wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chapter Subgraph 包装节点

    职责：
    1. 接收 Send API 传入的 state（ChapterState 格式）
    2. 调用 subgraph.ainvoke() 执行章节写作
    3. 只返回 completed_chapters，实现 state 隔离

    Args:
        state: Send API 传入的 ChapterState 数据

    Returns:
        只包含 completed_chapters 的 dict
    """
    chapter_id = state.get("chapter_id", 0)
    chapter_outline = state.get("chapter_outline")

    # 获取章节标题用于日志
    if hasattr(chapter_outline, "title"):
        chapter_title = chapter_outline.title
    else:
        chapter_title = f"Chapter {chapter_id}"

    logger.info(f"📝 [Wrapper] 开始执行章节 {chapter_id}: {chapter_title}")

    # 构建 ChapterState 输入
    subgraph_input = {
        "chapter_id": state["chapter_id"],
        "writer_role": state["writer_role"],
        "writer_profile": state["writer_profile"],
        "writing_principles": state["writing_principles"],
        "document_outline": state["document_outline"],
        "chapter_outline": state["chapter_outline"],
    }

    # 获取 subgraph 实例并执行
    subgraph = get_chapter_subgraph()
    result = await subgraph.ainvoke(subgraph_input)

    logger.success(f"✅ [Wrapper] 章节 {chapter_id} 执行完成")

    # 只返回需要合并到父图的字段
    # 这样 writer_role 等字段不会被传回父图，避免并发冲突
    return {
        "completed_chapters": result.get("completed_chapters", {})
    }
