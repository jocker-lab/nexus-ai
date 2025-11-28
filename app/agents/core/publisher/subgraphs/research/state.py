# -*- coding: utf-8 -*-
"""
@File    :   state.py
@Time    :   2025/11/5 08:43
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   Research Subgraph 状态定义
"""
import operator
from typing import List, Annotated, Optional
from typing_extensions import TypedDict


# ============= 主图状态 =============
class ResearcherState(TypedDict):
    """
    Research Subgraph 的主状态
    用于 plan_research 和 aggregate_results 节点
    """
    # 输入参数
    language: str  # 语言设置（如 "zh-CN", "en-US"）
    research_topics: List[str]  # 研究主题列表
    need_search: bool  # 是否需要使用搜索工具

    # 输出结果（使用 reducer 自动聚合）
    results: Annotated[List[dict], operator.add]  # 收集所有研究结果
    research_draft: str

# ============= 单任务状态 =============
class SingleResearchState(TypedDict):
    """
    单个研究任务的状态
    用于 execute_single_research_node 节点

    设计原则：
    - 只定义节点需要读取的字段（输入视图）
    - 不定义 results 字段（节点只写入，不读取）
    """
    language: str  # 语言设置
    current_research_topic: str  # 当前正在研究的主题
    need_search: bool  # 是否需要搜索