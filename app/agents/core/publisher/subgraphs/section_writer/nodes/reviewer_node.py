# -*- coding: utf-8 -*-
"""
@File    :   reviewer_node.py
@Time    :   2025/11/14 10:14
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
from typing import Dict, Any
from loguru import logger
from app.agents.core.publisher.subgraphs.section_writer.state import ChapterState
from app.agents.schemas.review_schema import ReviewResult
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from app.agents.prompts.template import render_prompt_template


async def review_draft(state: ChapterState) -> Dict[str, Any]:
    """
    【章节审查节点】- 使用 Structured Output 的审查者

    职责：
    1. 调用 LLM 对当前草稿进行多维度结构化评审
    2. 获取标准化的 ReviewResult（包含评分、问题列表、修改建议等）
    3. 记录本次审查结果到历史，并更新 revision_count

    注意：本节点只负责“评审”，不负责“决策是否修订”。
          决策逻辑统一放在外层的路由函数（decide_after_review）中，更符合 LangGraph 的状态机设计理念。
    """


    chapter_id = state["chapter_id"]
    chapter_title = state["chapter_outline"].title
    

    logger.info(f"📊 [Chapter {chapter_id}] 《{chapter_title}》 Reviewer: 开始审查...")

    # 初始化 LLM（这里建议后续改为从 config 中读取，便于切换模型）
    llm = init_chat_model("deepseek:deepseek-chat")

    system_message = render_prompt_template(
        "publisher_prompts/chapter_writing/chapter_review_system",
        {
            "language": state["document_outline"].language,
        },
    )

    user_message = render_prompt_template(
        "publisher_prompts/chapter_writing/chapter_review_task",
        state
    )
    try:

        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=user_message)
        ]

        # 绑定结构化输出（关键！确保返回的是 Pydantic 对象）
        structured_llm = llm.with_structured_output(ReviewResult)

        # 构造 Prompt（使用你已有的模板系统）


        # 异步调用，获取结构化结果
        review_result: ReviewResult = await structured_llm.ainvoke(messages)

        logger.success(
            f"✅ 审查完成 | 总分: {review_result.score}/100 | "
            f"决策: {review_result.status.upper()} | "
            f"审查问题说明: {review_result.general_feedback} | "
            f"问题数: {len(review_result.actionable_suggestions)}"
        )

    except Exception as exc:
        logger.error(f"❌ [Chapter {chapter_id}] 章节审查失败: {exc}", exc_info=True)

        # 失败时返回一个保守的、能让流程继续的安全默认结果
        review_result = ReviewResult(
            status="revise",
            score=40,
            general_feedback="【自动审查失败】由于 LLM 调用异常，系统无法完成正常评审，已标记为需要修订。",
            actionable_suggestions=[
                "请检查章节草稿是否包含异常格式（如超长代码块、特殊字符等）",
                "建议重新生成该章节草稿后再次提交审查"
            ],
        )

    # === 更新状态 ===
    current_revision_count = state.get("revision_count", 0) + 1

    logger.info(f"↳ 修订次数: {current_revision_count} ")

    return {
        "latest_review": review_result,  # 当前最新的审查结果（供路由节点决策使用）
        "revision_count": current_revision_count,  # 关键计数器，决定是否进入“强制通过”或“人工介入”
    }
