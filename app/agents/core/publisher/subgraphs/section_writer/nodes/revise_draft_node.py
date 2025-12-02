# -*- coding: utf-8 -*-
"""
@File    :   revise_draft_node.py
@Time    :   2025/11/20 21:42
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   章节修订节点 - 根据审查反馈修订草稿
"""

from typing import Dict, Any
from loguru import logger
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.core.publisher.subgraphs.section_writer.state import ChapterState
from app.agents.prompts.template import render_prompt_template


async def revise_draft(state: ChapterState) -> Dict[str, Any]:
    """
    【章节修订节点】- 根据审查反馈修订草稿

    职责：
    1. 获取当前草稿和审查反馈
    2. 调用 LLM 根据反馈修订草稿
    3. 返回修订后的草稿

    输入：
    - state["draft"]: 当前草稿内容
    - state["latest_review"]: 审查结果（包含 actionable_suggestions）

    输出：
    - draft: 修订后的草稿内容
    """
    chapter_id = state["chapter_id"]
    chapter_title = state["chapter_outline"].title
    revision_count = state.get("revision_count", 0)

    logger.info(f"📝 [Chapter {chapter_id}] 《{chapter_title}》 Reviser: 开始第 {revision_count} 次修订...")

    # 获取当前草稿和审查反馈
    current_draft = state.get("draft", "")
    latest_review = state.get("latest_review")

    if not current_draft:
        logger.warning(f"[Chapter {chapter_id}] 无草稿内容，跳过修订")
        return {}

    if not latest_review:
        logger.warning(f"[Chapter {chapter_id}] 无审查结果，跳过修订")
        return {}

    # 初始化 LLM
    llm = init_chat_model("deepseek:deepseek-chat", temperature=0.7)

    # 渲染 System Prompt
    system_prompt = render_prompt_template(
        "publisher_prompts/chapter_writing/chapter_revise_system",
        {
            "writer_role": state.get("writer_role", "专业写手"),
            "writer_profile": state.get("writer_profile", ""),
            "writing_principles": state.get("writing_principles", []),
            "language": state["document_outline"].language,
        }
    )

    # 渲染 User Prompt
    user_prompt = render_prompt_template(
        "publisher_prompts/chapter_writing/chapter_revise_task",
        {
            "draft": current_draft,
            "review_result": latest_review,
            "language": state["document_outline"].language,
            "chapter_outline": state["chapter_outline"],
            "document_outline": state["document_outline"],
        }
    )

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        logger.info(messages)

        response = await llm.ainvoke(messages)
        revised_draft = response.content.strip()

        logger.success(
            f"✅ [Chapter {chapter_id}] 修订完成 | "
            f"原字数: {len(current_draft)} | "
            f"修订后字数: {len(revised_draft)} | "
            f"处理建议数: {len(latest_review.actionable_suggestions)}"
            f"修订后的稿件: \n{revised_draft}"
        )

        return {
            "draft": revised_draft,
        }

    except Exception as e:
        logger.error(f"❌ [Chapter {chapter_id}] 修订失败: {e}", exc_info=True)
        # 修订失败时返回原草稿，让流程继续
        return {
            "draft": current_draft,
        }
