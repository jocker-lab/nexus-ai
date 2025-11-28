# -*- coding: utf-8 -*-
"""
@File    :   agent.py
@Time    :   2025/11/14 10:39
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   Document Writing Main Graph
"""
from langgraph.graph import StateGraph, END
from loguru import logger
from app.agents.core.publisher.writing.state import DocumentState
from app.agents.core.publisher.writing.nodes import (
    role_builder_node,
    chapter_aggregator,
    chapter_dispatcher,
    document_integrator,
    document_reviewer,
    document_reviser,
    chapter_subgraph_wrapper,
)

# === 配置常量 ===
MAX_REVISION_COUNT = 2  # 最大修订次数
PASS_SCORE_THRESHOLD = 85  # 通过分数阈值


def decide_after_review(state: DocumentState) -> str:
    """
    审查后的路由决策

    决策逻辑：
    1. 如果 status == "pass" 或 score >= 85 → 结束
    2. 如果已达到最大修订次数 → 强制结束
    3. 否则 → 进入修订流程
    """
    latest_review = state.get("latest_review")
    revision_count = state.get("revision_count", 0)

    if not latest_review:
        logger.warning("[Router] No review result, ending flow")
        return "end"

    # 检查是否通过
    if latest_review.status == "pass" or latest_review.score >= PASS_SCORE_THRESHOLD:
        logger.info(
            f"[Router] Document PASSED | "
            f"Score: {latest_review.score} | Status: {latest_review.status}"
        )
        return "end"

    # 检查修订次数
    if revision_count >= MAX_REVISION_COUNT:
        logger.warning(
            f"[Router] Max revisions reached ({MAX_REVISION_COUNT}), forcing end"
        )
        return "end"

    # 需要修订
    logger.info(
        f"[Router] Document needs revision | "
        f"Score: {latest_review.score} | Revision: {revision_count}/{MAX_REVISION_COUNT}"
    )
    return "revise"


def finalize_review(state: DocumentState) -> dict:
    """
    最终化审查结果节点 - 将 latest_review 转换为 document_review

    这是一个轻量级节点，仅做数据转换
    """
    latest_review = state.get("latest_review")

    if not latest_review:
        return {
            "document_review": {
                "status": "unknown",
                "overall_assessment": "No review performed",
            }
        }

    return {
        "document_review": {
            "status": "completed",
            "overall_assessment": latest_review.general_feedback,
            "score": latest_review.score,
            "final_status": latest_review.status,
            "suggestions_count": len(latest_review.actionable_suggestions),
        }
    }


def create_main_graph():
    """
    创建 Main Graph

    流程:
        role_builder → chapter_dispatcher → [Subgraphs...] → chapter_aggregator
        → document_integrator → document_reviewer → [revise loop] → finalize → END

    审查流程：
        document_reviewer → decide_after_review
            ├── "pass" → finalize_review → END
            └── "revise" → document_reviser → document_reviewer (loop)
    """
    # === 1. 创建 StateGraph ===
    main_graph = StateGraph(DocumentState)

    # === 2. 添加 Main Graph 节点 ===
    main_graph.add_node("role_builder_node", role_builder_node)
    main_graph.add_node("chapter_dispatcher", chapter_dispatcher)
    main_graph.add_node("chapter_aggregator", chapter_aggregator)
    main_graph.add_node("document_integrator", document_integrator)
    main_graph.add_node("document_reviewer", document_reviewer)
    main_graph.add_node("document_reviser", document_reviser)
    main_graph.add_node("finalize_review", finalize_review)

    # === 3. 添加 Subgraph 包装节点 ===
    main_graph.add_node("chapter_subgraph", chapter_subgraph_wrapper)

    # === 4. 设置入口点 ===
    main_graph.set_entry_point("role_builder_node")

    # === 5. 添加边 ===

    # 主流程边
    main_graph.add_edge("role_builder_node", "chapter_dispatcher")
    main_graph.add_edge("chapter_subgraph", "chapter_aggregator")
    main_graph.add_edge("chapter_aggregator", "document_integrator")
    main_graph.add_edge("document_integrator", "document_reviewer")

    # 审查后的条件路由
    main_graph.add_conditional_edges(
        "document_reviewer",
        decide_after_review,
        {
            "end": "finalize_review",
            "revise": "document_reviser",
        }
    )

    # 修订后返回审查
    main_graph.add_edge("document_reviser", "document_reviewer")

    # 最终化后结束
    main_graph.add_edge("finalize_review", END)

    # === 6. 编译 ===
    compiled_main_graph = main_graph.compile()

    return compiled_main_graph
