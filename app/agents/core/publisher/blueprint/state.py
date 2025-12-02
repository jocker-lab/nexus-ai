# -*- coding: utf-8 -*-
"""
@File    :   state.py
@Time    :   2025/10/31 20:34
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""

import operator
from typing import Annotated, List
from typing_extensions import TypedDict
from app.agents.schemas.blueprint_schema import Step, StepExecution


class PlanExecuteState(TypedDict):
    """
    工作流状态定义
    """
    language: str = 'zh-CN'
    max_research_topics: int  # RESEARCH 步骤最大 topics 数量，默认 5
    conversation_messages: Annotated[List, operator.add]
    pending_steps: List[Step]
    completed_steps: Annotated[List[StepExecution], operator.add]
    blueprint_draft: str
    response: str

