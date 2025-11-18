# -*- coding: utf-8 -*-
"""
@File    :   state.py
@Time    :   2025/11/5 08:43
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
import operator
from typing import List, Annotated, Optional
from typing_extensions import TypedDict


class ResearcherState(TypedDict):
    """
    Research Subgraph 的状态
    """
    # 输入
    research_topics: List[str]  # 研究主题列表
    need_search: bool  # 是否需要搜索
    language: str  # 语言设置

    # 中间状态（用于单个任务）
    current_topic: str                  # 当前正在处理的主题

    # 输出（收集结果）
    results: Annotated[List[dict], operator.add]  # 使用 add reducer 收集结果

    # ⭐⭐⭐ 修复：添加最终输出字段
    final_result: Optional[str]  # 格式化的最终结果字符串
    success_count: Optional[int]  # 成功的任务数
    total_count: Optional[int]  # 总任务数


