# -*- coding: utf-8 -*-
"""
Document Reviser - 文档修订节点

职责：
1. 获取当前文档和审查反馈
2. 调用 LLM 根据反馈修订文档
3. 返回修订后的文档

输入：
- state["document"]: 当前文档内容
- state["latest_review"]: 审查结果（包含 actionable_suggestions）

输出：
- document: 修订后的文档内容
"""
from datetime import datetime
from typing import Dict, Any
from loguru import logger
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.core.publisher.writing.state import DocumentState
from app.agents.prompts.template import render_prompt_template


async def document_reviser(state: DocumentState) -> Dict[str, Any]:
    """
    文档修订节点 - 根据审查反馈修订文档

    Args:
        state: DocumentState

    Returns:
        {"document": str}
    """
    logger.info("\n" + "=" * 60)
    logger.info("Document Reviser: 开始修订文档...")
    logger.info("=" * 60)

    revision_count = state.get("revision_count", 0)
    document = state.get("document", "")
    latest_review = state.get("latest_review")
    outline = state["document_outline"]

    if not document:
        logger.warning("  No document content, skipping revision")
        return {}

    if not latest_review:
        logger.warning("  No review result, skipping revision")
        return {}

    logger.info(f"  Revision #{revision_count}")
    logger.info(f"  Original document length: {len(document)} chars")
    logger.info(f"  Suggestions to address: {len(latest_review.actionable_suggestions)}")

    # === 渲染 Prompt ===
    system_prompt = render_prompt_template(
        "publisher_prompts/document_writing/document_revise_system",
        {
            "CURRENT_TIME": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "language": outline.language,
        }
    )

    user_prompt = render_prompt_template(
        "publisher_prompts/document_writing/document_revise_task",
        {
            "document": document,
            "general_feedback": latest_review.general_feedback,
            "actionable_suggestions": latest_review.actionable_suggestions,
            "language": outline.language,
        }
    )

    # === 调用 LLM ===
    llm = init_chat_model(
        "deepseek:deepseek-reasoner",
        max_tokens=16384,
        timeout=120,  # 推理模型耗时较长，加大超时
    )

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = await llm.ainvoke(messages)
        revised_document = response.content.strip()

        logger.success(
            f"  Revision completed | "
            f"Original: {len(document)} chars | "
            f"Revised: {len(revised_document)} chars | "
            f"Suggestions addressed: {len(latest_review.actionable_suggestions)}"
        )
        logger.info("=" * 60 + "\n")

        return {
            "document": revised_document,
        }

    except Exception as e:
        logger.error(f"  Revision failed: {e}", exc_info=True)
        logger.info("  Using original document")
        logger.info("=" * 60 + "\n")

        # 修订失败时返回原文档
        return {
            "document": document,
        }
