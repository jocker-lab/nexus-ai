# -*- coding: utf-8 -*-
"""
@File    :   agent.py
@Time    :   2025/11/14 10:14
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
from loguru import logger
from langgraph.graph import StateGraph, END
from app.agents.core.publisher.subgraphs.chapter_writing.state import ChapterState
from app.agents.core.publisher.subgraphs.chapter_writing.nodes import (
    chapter_content_writer,
    chapter_researcher,
    chapter_reviewer,
    chapter_finalizer
)



def create_chapter_subgraph():
    """
    创建 Chapter Subgraph - 修复版本

    流程:
        Research → Writer → Reviewer → decide
                     ↑                  ↓
                     └──── revise ──────┘
                                        ↓
                                    Finalizer → END
    """
    subgraph = StateGraph(ChapterState)

    # 添加节点
    subgraph.add_node("researcher_prompts", chapter_researcher)
    subgraph.add_node("writer", chapter_content_writer)
    subgraph.add_node("reviewer", chapter_reviewer)
    subgraph.add_node("finalizer", chapter_finalizer)

    # 入口
    subgraph.set_entry_point("researcher_prompts")

    # 固定边
    subgraph.add_edge("researcher_prompts", "writer")
    subgraph.add_edge("writer", "reviewer")

    # 条件边：审查后决策
    def decide_after_review(state: ChapterState) -> str:
        """
        决策逻辑（在 reviewer 节点之后调用）：

        注意：此时 revision_count 已经被 reviewer 增加过了
        - 第1次审查后：revision_count = 1
        - 第2次审查后：revision_count = 2
        - 第3次审查后：revision_count = 3

        决策规则：
        - revision_count > 2 → 强制通过（已经修订2次了）
        - 评分 >= 85 → 通过
        - 评分 < 85 → 修订
        """
        review_result = state.get("review_result")
        revision_count = state.get("revision_count", 0)

        if not review_result:
            raise ValueError("Missing review_result in state")

        score = review_result.overall_score

        logger.info(f"    ↳ [决策] 当前状态: 审查次数={revision_count}, 评分={score}")

        # 已达修订上限 → 强制通过
        # revision_count > 2 意味着已经经过了 2 次修订（第1次初稿 + 2次修订）
        if revision_count > 2:
            logger.info(f"    ↳ [决策] 通过 ✅ (已修订{revision_count-1}次，达到上限)")
            return "finalize"

        # 评分 >= 85 → 通过
        if score >= 85:
            logger.info(f"    ↳ [决策] 通过 ✅ (评分={score}，达标)")
            return "finalize"

        # 评分 < 85 → 修订
        logger.info(f"    ↳ [决策] 修订 🔄 (评分={score}，第{revision_count}次修订)")
        return "revise"

    subgraph.add_conditional_edges(
        "reviewer",
        decide_after_review,
        {
            "revise": "writer",  # 修订：回到 writer
            "finalize": "finalizer",  # 定稿
        }
    )

    # 定稿后结束
    subgraph.add_edge("finalizer", END)

    return subgraph.compile()