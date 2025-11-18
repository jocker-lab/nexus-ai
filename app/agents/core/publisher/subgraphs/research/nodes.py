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
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

from app.agents.core.publisher.subgraphs.research.state import ResearcherState
from app.agents.prompts.template import apply_prompt_template


def dispatch_research_tasks(state: ResearcherState):
    """
    入口节点：分发研究任务

    ⭐⭐⭐ 关键修复：使用 Command 包装 Send 对象列表
    """
    topics = state["research_topics"]
    need_search = state["need_search"]
    language = state["language"]

    logger.info(f"📚 分发 {len(topics)} 个研究任务进行并行处理")

    # 创建 Send 对象列表
    sends = [
        Send(
            "execute_single_research",
            {
                "current_topic": topic,
                "need_search": need_search,
                "language": language,
                "research_topics": topics,
                "results": []
            }
        )
        for topic in topics
    ]

    # ⭐⭐⭐ 关键修复：使用 Command 包装 Send 列表
    # 不能直接 return sends，必须用 Command
    return Command(goto=sends)


async def execute_single_research_node(state: ResearcherState):
    """
    执行节点：处理单个研究任务
    这个节点会被并行调用多次（每个任务一次）
    """
    # 导入工具（延迟导入避免循环依赖）
    try:
        from agents.tools.tavily_search import searcher
    except ImportError:
        # 如果路径不同，尝试其他路径
        try:
            from app.agents.tools.search.tavily_search import searcher
        except ImportError:
            logger.warning("无法导入 searcher，搜索功能将不可用")
            searcher = None

    topic = state["current_topic"]
    need_search = state["need_search"]
    language = state["language"]

    logger.info(f"🔍 执行研究任务: {topic}")

    system_prompt = apply_prompt_template("researcher/researcher", state)

    task_formatted = f"""
    Research the following topic:
    Topic: {topic}
    Please provide comprehensive information about this topic.
    response use {language}
    """
    # 使用支持流式的 LLM
    llm = init_chat_model("deepseek:deepseek-chat")

    try:
        if need_search and searcher:
            # 使用搜索工具
            logger.info(f"   🌐 使用搜索工具查询: {topic}")
            search_tools = [searcher]
            search_agent = create_deep_agent(
                llm,
                search_tools,
                system_prompt=system_prompt[0].content,
            )

            # 使用 ainvoke 支持异步和流式
            agent_response = await search_agent.ainvoke(
                {"messages": [HumanMessage(content=task_formatted)]}
            )
            response_content = agent_response['messages'][-1].content
            logger.success(f"   ✅ 搜索完成: {topic} ({len(response_content)} 字符)")

        else:
            # 直接使用 LLM 回答
            logger.info(f"   🤖 使用 LLM 直接回答: {topic}")
            response = await llm.ainvoke(task_formatted)
            response_content = response.content
            logger.success(f"   ✅ 回答完成: {topic} ({len(response_content)} 字符)")

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
    聚合节点：整理并返回所有研究结果
    """
    results = state.get("results", [])
    logger.success(f"🎉 研究任务全部完成，共 {len(results)} 个结果")

    # 格式化最终结果
    formatted_results = []
    success_count = sum(1 for r in results if r.get("success", False))

    for result_data in results:
        topic = result_data.get("topic", "Unknown")
        result = result_data.get("result", "")
        formatted_results.append(f"Topic: {topic}\nResult: {result}")

    final_result = "\n\n---\n\n".join(formatted_results)

    logger.info(f"📊 成功: {success_count}/{len(results)}, 总计 {len(final_result)} 字符")

    # 返回格式化的字符串结果
    return {
        "final_result": final_result,
        "success_count": success_count,
        "total_count": len(results)
    }
