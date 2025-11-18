# -*- coding: utf-8 -*-
"""
@File    :   thinking_tools.py
@Time    :   2025/10/28 16:08
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
from pydantic import Field
from langchain.tools import tool

@tool("criticize")
def criticize(
        criticism: str = Field(..., description="Constructive review and feedback on your current approach")) -> str:
    """
    Review and validate your reasoning and approach.

    Use this tool when you need to:
    - Validate your current strategy
    - Identify gaps or potential issues
    - Refine your approach before continuing
    - Provide self-feedback and improvements

    This tool does not fetch new information or modify data; it only records your review.
    """
    return criticism

@tool("plan")
def plan(plan: str = Field(..., description="Detailed plan of the next investigative steps")) -> str:
    """
    Create and document your investigation plan.

    Use this tool when you need to:
    - Outline your overall strategy
    - Break down complex tasks into steps
    - Decide which tools to use and in what sequence
    - Document your approach before execution

    This tool does not fetch new information or modify data; it only records your plan.
    """
    return plan


@tool("think")
def think(thought: str = Field(..., description="Your reasoning or reflection on the problem")) -> str:
    """
    Leverage your reasoning and thinking process.

    Use this tool when you need to:
    - Analyze and reason through information
    - Reflect on your findings
    - Document your thought process
    - Store reasoning in memory for later reference

    This tool does not fetch new information or modify data; it only records your thoughts.
    """
    return thought


