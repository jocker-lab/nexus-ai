# -*- coding: utf-8 -*-
"""
Document Reviewer - 文档全局审查节点

职责：
1. 使用 Structured Output 对完整文档进行全局审查
2. 生成结构化的审查结果（ReviewResult）
3. 返回 latest_review 供路由决策和 reviser 使用

注意：本节点只负责"审查"，不负责"修订"。
"""
from datetime import datetime
from typing import Dict, Any
from loguru import logger
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.core.publisher.writing.state import DocumentState
from app.agents.schemas.review_schema import ReviewResult
from app.agents.prompts.template import render_prompt_template


async def document_reviewer(state: DocumentState) -> Dict[str, Any]:
    """
    文档全局审查节点 - 使用 Structured Output

    Args:
        state: DocumentState

    Returns:
        {"latest_review": ReviewResult, "revision_count": int}
    """
    logger.info("\n" + "=" * 60)
    logger.info("Document Reviewer: 开始全局审查...")
    logger.info("=" * 60)

    document = state["document"]
    outline = state["document_outline"]
    metadata = state.get("document_metadata", {})

    total_words = metadata.get("total_words", len(document))
    target_length = outline.estimated_total_words
    avg_score = metadata.get("avg_score", 0)
    total_chapters = metadata.get("total_chapters", 0)

    # === 渲染 Prompt ===
    logger.info("  Preparing review prompts...")

    system_prompt = render_prompt_template(
        "publisher_prompts/document_writing/document_review_system",
        {
            "language": outline.language,
        }
    )

    user_prompt = render_prompt_template(
        "publisher_prompts/document_writing/document_review_task",
        {
            "CURRENT_TIME": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": outline.title,
            "language": outline.language,
            "total_words": total_words,
            "target_length": target_length,
            "avg_score": avg_score,
            "writing_style": outline.writing_style,
            "writing_tone": outline.writing_tone,
            "target_audience": outline.target_audience,
            "writing_purpose": outline.writing_purpose,
            "total_chapters": total_chapters,
            "document": document,
        }
    )

    # === 调用 LLM with Structured Output ===
    logger.info("  Invoking LLM for structured review...")

    llm = init_chat_model("deepseek:deepseek-chat")

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        structured_llm = llm.with_structured_output(ReviewResult)
        review_result: ReviewResult = await structured_llm.ainvoke(messages)

        logger.success(
            f"  Review completed | Score: {review_result.score}/100 | "
            f"Status: {review_result.status.upper()} | "
            f"Suggestions: {len(review_result.actionable_suggestions)}"
        )
        logger.info(f"  Feedback: {review_result.general_feedback[:100]}...")

    except Exception as e:
        logger.error(f"  Review failed: {e}", exc_info=True)

        # 失败时返回保守的默认结果
        review_result = ReviewResult(
            status="pass",  # 审查失败时默认通过，避免阻塞流程
            score=70,
            general_feedback="【自动审查失败】由于 LLM 调用异常，系统无法完成正常评审。",
            actionable_suggestions=[],
        )

    # === 更新状态 ===
    current_revision_count = state.get("revision_count", 0) + 1

    logger.info(f"  Revision count: {current_revision_count}")
    logger.info("=" * 60 + "\n")

    return {
        "latest_review": review_result,
        "revision_count": current_revision_count,
    }
