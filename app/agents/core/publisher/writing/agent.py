# -*- coding: utf-8 -*-
"""
@File    :   agent.py
@Time    :   2025/11/14 10:39
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   Document Writing Main Graph

简化流程（v2）：
    role_builder → chapter_dispatcher → [Subgraphs...] → chapter_aggregator
    → document_integrator → document_finalizer → END

说明：
    - 移除了 document_reviewer 和 document_reviser 节点
    - 章节级别已完成审查和修订，文档级别不再重复
    - document_finalizer 使用 with_structured_output 提取元数据
"""
from langgraph.graph import StateGraph, END
from loguru import logger
from app.agents.core.publisher.writing.state import DocumentState
from app.agents.core.publisher.writing.nodes import (
    role_builder_node,
    chapter_aggregator,
    chapter_dispatcher,
    document_integrator,
    document_finalizer,
    chapter_subgraph_wrapper,
)


def create_main_graph():
    """
    创建 Main Graph（简化版）

    流程:
        role_builder → chapter_dispatcher → [Subgraphs...] → chapter_aggregator
        → document_integrator → document_finalizer → END

    节点说明：
        - role_builder_node: 构建写作角色和风格
        - chapter_dispatcher: 分发章节写作任务
        - chapter_subgraph: 章节写作子图（包含审查修订）
        - chapter_aggregator: 聚合已完成章节
        - document_integrator: 智能整合文档（LLM驱动）
        - document_finalizer: 提取元数据（description/category/tags/word_count）
    """
    logger.info("📖 [Writing Agent] 创建文档写作图...")

    # === 1. 创建 StateGraph ===
    main_graph = StateGraph(DocumentState)

    # === 2. 添加节点 ===
    main_graph.add_node("role_builder_node", role_builder_node)
    main_graph.add_node("chapter_dispatcher", chapter_dispatcher)
    main_graph.add_node("chapter_aggregator", chapter_aggregator)
    main_graph.add_node("document_integrator", document_integrator)
    main_graph.add_node("document_finalizer", document_finalizer)

    # === 3. 添加 Subgraph 包装节点 ===
    main_graph.add_node("chapter_subgraph", chapter_subgraph_wrapper)

    # === 4. 设置入口点 ===
    main_graph.set_entry_point("role_builder_node")

    # === 5. 添加边（线性流程） ===
    main_graph.add_edge("role_builder_node", "chapter_dispatcher")
    main_graph.add_edge("chapter_subgraph", "chapter_aggregator")
    main_graph.add_edge("chapter_aggregator", "document_integrator")
    main_graph.add_edge("document_integrator", "document_finalizer")
    main_graph.add_edge("document_finalizer", END)

    # === 6. 编译 ===
    compiled_main_graph = main_graph.compile()

    logger.info("  ✓ 文档写作图编译完成")
    logger.info("    流程: role_builder → dispatcher → subgraphs → aggregator → integrator → finalizer → END\n")

    return compiled_main_graph
