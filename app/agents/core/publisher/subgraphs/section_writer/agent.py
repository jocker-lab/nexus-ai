# -*- coding: utf-8 -*-
"""
@File    :   agent.py
@Time    :   2025/11/14 10:14
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   Section Writer Subgraph - 章节写作子图

Updated: 2025/11/27
- 使用 chapter_content_generation subgraph 替换 researcher + writer 节点
- chapter_content_generation 已包含搜索和写作的迭代循环
"""
from typing import Dict, Any
from loguru import logger
from langgraph.graph import StateGraph, END
from app.agents.core.publisher.subgraphs.section_writer.state import ChapterState
from app.agents.core.publisher.subgraphs.section_writer.nodes import (
    review_draft,
    chapter_finalizer,
    revise_draft
)
from app.agents.core.publisher.subgraphs.chapter_content_generation.agent import (
    create_iterative_chapter_subgraph
)


# 缓存 chapter_content_generation subgraph 实例
_content_generation_subgraph = None


def get_content_generation_subgraph():
    """懒加载 chapter_content_generation subgraph"""
    global _content_generation_subgraph
    if _content_generation_subgraph is None:
        _content_generation_subgraph = create_iterative_chapter_subgraph()
    return _content_generation_subgraph


async def content_generation_node(state: ChapterState) -> Dict[str, Any]:
    """
    章节内容生成节点 - 调用 chapter_content_generation subgraph

    该节点封装了 chapter_content_generation subgraph，包含：
    - 搜索查询生成
    - 并行搜索执行
    - 基于素材的写作
    - 素材完整性评估和迭代

    Input: ChapterState (包含 chapter_outline, writer 上下文等)
    Output: {"draft": str} - 生成的章节草稿
    """
    chapter_id = state.get("chapter_id", 0)
    chapter_outline = state.get("chapter_outline")
    chapter_title = getattr(chapter_outline, "title", f"Chapter {chapter_id}")

    logger.info(f"📝 [Chapter {chapter_id}] 开始内容生成：{chapter_title}")

    # 构建 subgraph 输入状态
    subgraph_input = {
        "chapter_id": chapter_id,
        "chapter_outline": chapter_outline,
        # 传递写作上下文
        "document_outline": state.get("document_outline"),
        "writer_role": state.get("writer_role"),
        "writer_profile": state.get("writer_profile"),
        "writing_principles": state.get("writing_principles"),
        # 初始化迭代状态
        "iteration": 0,
        "search_results": [],
        "draft": "",
    }

    # 执行 chapter_content_generation subgraph
    subgraph = get_content_generation_subgraph()
    result = await subgraph.ainvoke(subgraph_input)

    # 提取结果
    draft = result.get("final_content") or result.get("draft", "")

    logger.success(f"✅ [Chapter {chapter_id}] 内容生成完成，字数: {len(draft)}")

    return {
        "draft": draft
    }


def create_chapter_subgraph():
    """
    创建 Chapter Subgraph

    流程:
        content_generation → Reviewer → decide
                               ↑          ↓
                               └── revise ─┤
                                           ↓
                                       Finalizer → END

    content_generation 节点包含：
        - 搜索查询生成 + 并行搜索
        - 基于素材的写作
        - 素材完整性评估和迭代循环

    决策逻辑（基于 latest_review.status）:
        - status == "pass" → finalize（通过）
        - status == "revise" 且 revision_count <= 2 → revise（修订）
        - status == "revise" 且 revision_count > 2 → finalize（强制通过）
    """
    subgraph = StateGraph(ChapterState)

    # 添加节点
    subgraph.add_node("content_generation", content_generation_node)  # 替换原来的 researcher + writer
    subgraph.add_node("reviewer", review_draft)
    subgraph.add_node("reviser", revise_draft)
    subgraph.add_node("finalizer", chapter_finalizer)

    # 入口
    subgraph.set_entry_point("content_generation")

    # 固定边
    subgraph.add_edge("content_generation", "reviewer")

    # 条件边：审查后决策
    def decide_after_review(state: ChapterState) -> str:
        """
        决策逻辑（在 reviewer 节点之后调用）：

        基于 latest_review.status 进行判断：
        - status == "pass" → 直接通过
        - status == "revise" → 检查修订次数
            - revision_count > 2 → 强制通过（已修订2次）
            - 否则 → 进入修订流程
        """
        latest_review = state.get("latest_review")
        revision_count = state.get("revision_count", 0)

        if not latest_review:
            raise ValueError("Missing latest_review in state")

        status = latest_review.status
        score = latest_review.score

        logger.info(f"    ↳ [决策] 当前状态: 审查次数={revision_count}, 评分={score}, 状态={status}")

        # 审查通过 → 直接定稿
        if status == "pass":
            logger.info(f"    ↳ [决策] 通过 ✅ (评审结果: pass, 评分={score})")
            return "finalize"

        # 审查需要修订，但已达修订上限 → 强制通过
        if revision_count > 2:
            logger.info(f"    ↳ [决策] 强制通过 ✅ (已修订{revision_count}次，达到上限)")
            return "finalize"

        # 审查需要修订，且未达上限 → 进入修订
        logger.info(f"    ↳ [决策] 修订 🔄 (评分={score}，第{revision_count}次修订)")
        return "revise"

    subgraph.add_conditional_edges(
        "reviewer",
        decide_after_review,
        {
            "revise": "reviser",   # 修订：进入 reviser 节点
            "finalize": "finalizer",  # 定稿
        }
    )

    # 修订后重新进入 reviewer
    subgraph.add_edge("reviser", "reviewer")

    # 定稿后结束
    subgraph.add_edge("finalizer", END)

    return subgraph.compile()
