# -*- coding: utf-8 -*-
"""
@File    :   chapter_reviewer.py
@Time    :   2025/11/14 10:14
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
from typing import Dict, Any
from loguru import logger
from app.agents.core.publisher.subgraphs.chapter_writing.state import ChapterState
from app.agents.schemas.review_schema import ChapterReviewResult
from langchain.chat_models import init_chat_model
from app.agents.prompts.template import apply_prompt_template, render_prompt_template


async def chapter_reviewer(state: ChapterState) -> Dict[str, Any]:
    """
    章节审查节点 - 使用 Structured Output

    职责：
    1. 多维度评分章节质量
    2. LLM 决策是否需要修订
    3. 生成修订指令
    """
    from app.agents.schemas.review_schema import DimensionScore, Issue

    chapter_id = state["chapter_id"]
    chapter_title = state["chapter_outline"].title  # ✅ Bug #1: 修复字段访问

    logger.info(f"  📊 [Chapter {chapter_id} : title {chapter_title}] Reviewer: 开始审查...")

    llm = init_chat_model("deepseek:deepseek-chat")

    # === 1. LLM 评审（使用 Structured Output）===
    try:
        llm_with_structure = llm.with_structured_output(ChapterReviewResult)

        # 使用 apply_prompt_template
        messages = apply_prompt_template(
            "chapter_writing/chapter_reviewer",
            {
                "chapter_id": chapter_id,
                "chapter_outline": state["chapter_outline"],
                "document_outline": state["document_outline"],
                "draft_content": state["draft_content"],
                "target_word_count": state["target_word_count"],
                "word_count": state["word_count"],
                "revision_count": state.get("revision_count", 0),
            }
        )
        print(messages)

        # ✅ Bug #2: 修复变量名（使用 messages 而非 review_prompt）
        review_result = await llm_with_structure.ainvoke(messages)

        # ✅ Bug #3: 修复字段名（overall_score 而非 score）
        logger.info(f"    ↳ 总分: {review_result.overall_score}/100\n")

    except Exception as e:
        logger.error(f"    ❌ 审查失败: {str(e)}\n", exc_info=True)

        # 返回默认审查结果
        review_result = ChapterReviewResult(
            overall_score=50,
            dimensions={
                "content_coverage": DimensionScore(score=50, assessment="fair"),
                "content_depth": DimensionScore(score=50, assessment="fair"),
                "structure_logic": DimensionScore(score=50, assessment="fair"),
                "language_quality": DimensionScore(score=50, assessment="fair"),
                "format": DimensionScore(score=50, assessment="fair"),
                "length": DimensionScore(score=50, assessment="fair"),
            },
            issues=[
                Issue(
                    dimension="content_coverage",
                    severity="critical",
                    location="Entire chapter",
                    problem=f"Review process failed: {str(e)}",
                    suggestion="Check chapter content format or contact administrator"
                )
            ],
            summary="Review failed. Returning default result. Please check chapter content."
        )

    # === 2. 返回评审结果 ===
    # 注意：决策逻辑已移至 agent.py 的路由函数中
    # Reviewer 只负责评分和发现问题，不负责决定是否修订

    # ✅ 修复：每次审查后都增加 revision_count
    # 这样 decide_after_review 函数就能看到正确的修订次数
    current_revision_count = state.get("revision_count", 0)
    new_revision_count = current_revision_count + 1

    logger.info(f"    ↳ 修订计数: {current_revision_count} → {new_revision_count}")

    return {
        "revision_history": [review_result],
        "review_result": review_result,
        "revision_count": new_revision_count,  # ✅ 每次审查后增加
    }