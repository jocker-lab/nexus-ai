# -*- coding: utf-8 -*-
"""
@File    :   document_writing_role_builder.py
@Time    :   2025/11/24 10:50
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
from loguru import logger
from typing import Dict, Any
from pydantic import ValidationError
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage


from app.agents.core.publisher.writing.state import DocumentState
from app.agents.prompts.template import render_prompt_template
from app.agents.schemas.document_writing_role import TechnicalWriterRole


async def role_builder_node(state: DocumentState) -> Dict[str, Any]:
    """
    LangGraph节点：使用LLM生成技术写作专家角色

    Args:
        state: 当前状态，包含role_requirements和domain

    Returns:
        更新后的状态，包含expert_role
    """
    print(state)
    logger.debug(f"🔧 开始构建角色 - 领域: {state['document_outline'].title}")

    # 初始化LLM
    llm = init_chat_model("deepseek:deepseek-chat", temperature=0.8)

    # 使用structured output
    llm_with_structure = llm.with_structured_output(TechnicalWriterRole)

    # 构建prompt
    system_prompt = render_prompt_template("publisher_prompts/document_writing/document_writing_role_select_system",
                                           {
                                               "language": state['document_outline'].language,

                                           })
    user_prompt = render_prompt_template("publisher_prompts/document_writing/document_writing_role_select_user",
                                         {
                                             "outline" : state['document_outline'],
                                         })

    try:
        # 1. 构造 Prompt (建议抽离 Prompt 逻辑，保持节点纯净)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # 2. 调用 LLM (确保 llm_with_structure 已经绑定了 with_structured_output)
        # 增加 timeout 防止无限等待
        result = await llm_with_structure.ainvoke(messages)

        logger.info(f"✅ [RoleGen] 角色创建成功: {result.role}")
        logger.info(f"✅ [RoleGen] 角色写作原则创建成功: {result.writing_principles}")

        # 4. 只返回需要更新的状态字段 (LangGraph 会自动 Merge)
        return {
            "writer_role": result.role,
            "writer_profile": result.profile,
            "writing_principles": result.writing_principles,  # 清空之前的错误
        }

    except ValidationError as e:
        logger.warning(f"⚠️ [RoleGen] 数据校验失败: {e}")
        # 针对 Pydantic 校验失败，可能需要返回特定标志让上层决定是否重试
        raise e

    except Exception as e:
        logger.error(f"❌ [RoleGen] 失败: {e}")
        # 💥 关键点：这里直接抛出异常！
        # 不要返回 {"success": False}，因为 state 里没有这个字段。
        # 抛出异常后，LangGraph 会根据配置的策略决定是 重试 还是 终止。
        raise e
