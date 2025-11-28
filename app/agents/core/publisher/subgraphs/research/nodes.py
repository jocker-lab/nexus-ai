# -*- coding: utf-8 -*-
"""
@File    :   nodes.py
@Time    :   2025/11/5 08:42
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
from langchain_core.messages import HumanMessage
from loguru import logger
from datetime import datetime

from langgraph.types import Send, Command
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model


from app.agents.tools.search.tavily_search import searcher
from app.agents.core.publisher.subgraphs.research.state import ResearcherState, SingleResearchState
from app.agents.prompts.template import apply_prompt_template, render_prompt_template


def plan_research(state: ResearcherState) -> list:
    """
    入口节点：将研究任务分发为并行执行的子任务

    工作流程：
    1. 读取 research_topics 列表
    2. 为每个 topic 创建一个 Send 对象
    3. 返回 Send 列表，LangGraph 自动并行执行

    Args:
        state: ResearcherState - 包含所有研究主题

    Returns:
        List[Send] - 并行任务列表
    """
    topics = state["research_topics"]
    need_search = state["need_search"]
    language = state["language"]

    logger.info(f"📚 开始分发 {len(topics)} 个研究任务")

    # 创建并行任务（LangGraph 1.0 原生支持）
    sends = [
        Send(
            "execute_single_research",  # 目标节点名（必须与 add_node 一致）
            {
                "current_research_topic": topic,
                "need_search": need_search,
                "language": language
            }
        )
        for topic in topics
    ]

    logger.info(f"✅ 分发完成，将并行执行 {len(sends)} 个任务")
    return Command(goto=sends)



async def execute_single_research_node(state: SingleResearchState):
    """
    执行节点：处理单个研究任务

    此节点会被并行调用多次（每个主题一次）

    工作流程：
    1. 从状态中读取 current_research_topic
    2. 根据 need_search 决定是否使用搜索工具
    3. 调用 LLM 生成研究结果
    4. 返回结果（自动聚合到主状态的 results 字段）

    Args:
        state: SingleResearchState - 单任务状态

    Returns:
        dict - 包含 results 字段的字典
    """

    # 读取任务参数
    topic = state["current_research_topic"]
    language = state["language"]

    logger.info(f"🔍 执行研究任务: {topic}")

    system_prompt = render_prompt_template("researcher_prompts/researcher", state)

    task_prompt = f"""
    Research the following topic and provide comprehensive information:

    Topic: {topic}

    Requirements:
    - Provide detailed and accurate information
    - Include key facts, concepts, and relevant context
    - Response language: {language}
    """
    # 使用支持流式的 LLM
    llm = init_chat_model("deepseek:deepseek-chat")

    try:

        # 使用搜索工具
        logger.info(f"   🌐 使用搜索工具查询: {topic}")
        search_tools = [searcher]
        search_agent = create_agent(
            llm,
            search_tools,
            system_prompt=system_prompt,
        )

        # 使用 ainvoke 支持异步和流式
        agent_response = await search_agent.ainvoke(
            {"messages": [HumanMessage(content=task_prompt)]}
        )
        response_content = agent_response['messages'][-1].content
        logger.success(f"   ✅ 搜索完成: {topic} ({len(response_content)} 字符)")

        # 返回结果到 results 列表（会被 operator.add 自动聚合）
        return {
            "results": [{
                "topic": topic,
                "result": response_content,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }]
        }


    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        error_type = type(e).__name__
        error_message = str(e)

        logger.error(f"   ❌ 研究失败: {topic}")
        logger.error(f"   错误类型: {error_type}")
        logger.error(f"   错误信息: {error_message}")
        logger.error(f"   完整堆栈:\n{error_traceback}")
        logger.error(f"   ❌ 研究失败: {topic} - {e}")
        return {
            "results": [{
                "topic": topic,
                "result": f"Error: {str(e)}",
                "success": False,
                "timestamp": datetime.now().isoformat()
            }]
        }


def aggregate_results(state: ResearcherState):
    """
    聚合节点：整理所有研究结果并格式化输出

    工作流程：
    1. 从 state.results 中读取所有任务结果
    2. 统计成功/失败数量
    3. 格式化为易读的字符串

    Args:
        state: ResearcherState - 包含所有聚合后的结果

    Returns:
        dict - 包含 final_result, success_count, total_count
    """
    results = state.get("results", [])
    total = len(results)
    success = sum(1 for r in results if r.get("success", False))

    logger.success(f"🎉 研究任务全部完成！成功: {success}/{total}")


    # 格式化最终结果
    formatted_parts = []
    for i, result_data in enumerate(results, 1):
        topic = result_data.get("topic", "Unknown")
        result = result_data.get("result", "")
        status = "✅" if result_data.get("success") else "❌"

        formatted_parts.append(
            f"{status} 任务 {i}: {topic}\n"
            f"{'=' * 60}\n"
            f"{result}\n"
        )

    final_result = "\n\n".join(formatted_parts)

    logger.info(f"📊 最终报告生成完成，总计 {len(final_result)} 字符")

    return {
        "research_draft": final_result,
    }