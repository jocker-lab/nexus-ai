# -*- coding: utf-8 -*-
"""
@File    :   agent.py
@Time    :   2025/11/14 10:39
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
from langgraph.graph import StateGraph, END
from app.agents.core.publisher.writing.state import DocumentState
from app.agents.core.publisher.writing.nodes import (
    chapter_aggregator,
    chapter_dispatcher,
    document_integrator,
    document_reviewer
)

from app.agents.core.publisher.subgraphs.chapter_writing.agent import create_chapter_subgraph

def create_main_graph():
    """
    创建 Main Graph

    流程:
        Chapter Dispatcher → [Subgraphs...] → Aggregator
        → Document Integrator → Global Reviewer → END
    """
    # === 1. 创建 StateGraph ===
    main_graph = StateGraph(DocumentState)

    # === 2. 添加 Main Graph 节点 ===
    main_graph.add_node("chapter_dispatcher", chapter_dispatcher)
    main_graph.add_node("chapter_aggregator", chapter_aggregator)
    main_graph.add_node("document_integrator", document_integrator)
    main_graph.add_node("document_reviewer", document_reviewer)

    # === 3. 添加 Subgraph ===
    chapter_subgraph = create_chapter_subgraph()
    main_graph.add_node("chapter_subgraph", chapter_subgraph)

    # === 4. 设置入口点 ===
    main_graph.set_entry_point("chapter_dispatcher")

    # === 5. 添加边 ===

    # 关键修复：chapter_subgraph 完成后去 aggregator，而不是 dispatcher 直接去 aggregator
    main_graph.add_edge("chapter_subgraph", "chapter_aggregator")

    main_graph.add_edge("chapter_aggregator", "document_integrator")
    main_graph.add_edge("document_integrator", "document_reviewer")
    main_graph.add_edge("document_reviewer", END)

    # === 6. 编译 ===
    compiled_main_graph = main_graph.compile()

    return compiled_main_graph