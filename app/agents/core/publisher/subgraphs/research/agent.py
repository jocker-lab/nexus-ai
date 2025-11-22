# -*- coding: utf-8 -*-
"""
@File    :   agent.py
@Time    :   2025/11/5 08:41
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
from loguru import logger
from typing import List
from langgraph.graph import StateGraph, START, END

from app.agents.core.publisher.subgraphs.research.nodes import (
    dispatch_research_tasks,
    execute_single_research_node,
    aggregate_results
)

from app.agents.core.publisher.subgraphs.research.state import ResearcherState


def build_research_subgraph():
    """
    构建 Research Subgraph

    工作流：
    START → dispatch → execute_single (并行) → aggregate → END
    """
    logger.info("🏗️  构建 Research Subgraph")

    workflow = StateGraph(ResearcherState)

    # 添加节点
    workflow.add_node("dispatch", dispatch_research_tasks)
    workflow.add_node("execute_single_research", execute_single_research_node)
    workflow.add_node("aggregate", aggregate_results)

    # 定义边
    workflow.add_edge(START, "dispatch")
    # dispatch 使用 Command(goto=sends)，LangGraph 会自动处理
    workflow.add_edge("execute_single_research", "aggregate")
    workflow.add_edge("aggregate", END)

    logger.success("✅ Research Subgraph 构建完成")

    return workflow.compile()


async def run_research_subgraph(topics: List[str], need_search: bool, language: str = "zh-CN", writing_priority: str = "normal") -> str:
    """
    便捷函数：执行研究 subgraph

    Args:
        topics: 研究主题列表
        need_search: 是否需要搜索
        language: 语言设置
        writing_priority: 章节优先级 ("low", "normal", "high", "critical")

    Returns:
        格式化的研究结果字符串
    """
    subgraph = build_research_subgraph()

    initial_state = {
        "research_topics": topics,
        "need_search": need_search,
        "language": language,
        "writing_priority": writing_priority,
        "results": []
    }

    result = await subgraph.ainvoke(initial_state)

    return result.get("final_result", "No results generated")