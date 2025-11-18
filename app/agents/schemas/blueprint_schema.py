# -*- coding: utf-8 -*-
"""
@File    :   blueprint_schema.py
@Time    :   2025/10/31 20:37
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""

from enum import Enum
from typing import Union, List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


class CoordinatorDecision(BaseModel):
    """
    Cognibot's decision on how to handle the user request.
    """
    next_action: Literal["reply_and_end", "handoff_to_planner"] = Field(
        description=(
            "'reply_and_end': Respond directly for simple queries, rejections, "
            "or when gathering more information. "
            "'handoff_to_planner': Transfer to planner when writing task is fully specified."
        )
    )

    message: str = Field(
        description=(
            "The response to send to the user. Can be a greeting, answer, "
            "clarifying question, rejection, or handoff confirmation."
        )
    )

    language: Literal["en-US", "zh-CN"] = Field(
        description="Detected language of user's input to maintain consistency."
    )

    # 内部路由映射
    @property
    def goto(self) -> Literal["__end__", "planner"]:
        return "__end__" if self.next_action == "reply_and_end" else "planner"


class StepType(str, Enum):
    # === 第一层：核心阶段分类 ===
    RESEARCH = "research"                          # 信息检索与资料收集阶段
    HUMAN_INVOLVEMENT = "human_involvement"        # 需要人类参与决策的阶段
    # === 第三层：蓝图优化与整合 ===
    WRITING_BLUEPRINT = "writing_blueprint"  # 蓝图优化（综合审查与质量提升）


class Step(BaseModel):
    """
    执行步骤的数据结构
    """
    step_type: StepType = Field(..., description="Indicates the nature of the step")
    target: str = Field(..., description="A concise, action-oriented title that describes the step's objective. ")
    actions: Union[str, List[str]] = Field(
        ...,
        description=(
            "Specific executable actions or tasks to be performed in this step. "
            "For RESEARCH steps, provide a list of concrete search topics (List[str]). "
            "For other step types, provide a single action description string (str) "
            "that clearly outlines the operation or decision to be carried out."
        )
    )

class StepExecution(BaseModel):
    """步骤执行记录（包含结果）"""
    step: Step                          # 步骤定义
    execution_res: str                  # 执行结果
    status: str = "completed"           # completed / failed / skipped


class Plan(BaseModel):
    """
    规划的步骤数据结构，包含不同步骤的列表
    """

    language: str = Field(
        ..., description="e.g. 'en-US' or 'zh-CN', based on the user's language"
    )
    thought: str = Field(default="", description="Thinking process for the plan")
    has_enough_context: bool
    steps: List[Step] = Field(
        description="Different steps to follow with their types and descriptions"
    )


class ReplanSteps(BaseModel):

    """
    重新规划的步骤列表
    """
    reasoning: str = Field(description="Explanation of the decision")
    steps: List[Step] = Field(description="Updated steps (empty if complete)")


