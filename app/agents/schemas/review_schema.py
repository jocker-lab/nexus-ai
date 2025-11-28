# -*- coding: utf-8 -*-
"""
@File    :   review_schema.py
@Time    :   2025/11/17 14:06
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Dict


class ReviewResult(BaseModel):
    """
        结构化的审查结果，用于驱动路由和修改
        """
    # 1. 核心决策：决定流程走向
    status: Literal["pass", "revise"] = Field(
        description="决策结果：如果内容符合要求且无重大错误，选 pass；否则选 revise"
    )

    # 2. 量化评分：用于分析或作为辅助阈值
    score: int = Field(
        description="0-100分。85分以上通常可以通过。",
        ge=0, le=100
    )

    # 3. 宏观评价：给人类看的，或者作为 Rewriter 的背景信息
    general_feedback: str = Field(
        description="对章节整体质量的简短评价，包括优点和主要缺陷。"
    )

    # 4. 【关键】可执行的修改建议：Rewriter 的直接指令列表
    # Rewriter 不需要看散文，只需要看这个列表
    actionable_suggestions: List[str] = Field(
        description="具体、明确的修改指令列表。例如：'删除第二段的重复内容'，'补充关于2023年的数据'。",
        default=[]
    )




class SuggestedFix(BaseModel):
    """Suggested fix for document issues"""

    location: str = Field(
        ...,
        description="Location of the issue (e.g., 'Chapter 2, Section 3', 'Between Chapter 1 and 2')"
    )

    issue_type: Literal["redundancy", "terminology", "coherence", "other"] = Field(
        ...,
        description="Type of issue"
    )

    description: str = Field(
        ...,
        description="Description of the issue"
    )

    suggested_change: str = Field(
        ...,
        description="Recommended change or fix"
    )


class GlobalReviewResult(BaseModel):
    """Global document review result with structured output"""

    overall_assessment: Literal["excellent", "good", "acceptable", "needs_revision"] = Field(
        ...,
        description="Overall document quality assessment"
    )

    coherence_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Coherence and flow score across chapters (0-100)"
    )

    redundancy_issues: List[str] = Field(
        default_factory=list,
        description="List of redundancy issues found across chapters"
    )

    terminology_issues: List[str] = Field(
        default_factory=list,
        description="List of terminology inconsistency issues"
    )

    suggested_fixes: List[SuggestedFix] = Field(
        default_factory=list,
        description="List of suggested fixes for identified issues"
    )

    recommendation: Literal["approve", "minor_fixes", "major_revision"] = Field(
        ...,
        description="Recommended action: approve (publish as-is), minor_fixes (auto-apply fixes), major_revision (needs manual work)"
    )


class CopyeditorResult(BaseModel):
    """AI Copyeditor 的结构化输出"""

    overall_assessment: Literal["excellent", "good", "acceptable", "needs_revision"] = Field(
        ...,
        description="Overall quality assessment of the document"
    )

    strengths: List[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Key strengths of the document (2-5 points)"
    )

    improvements_made: List[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Key improvements applied to the document (2-5 points)"
    )

    edited_document: str = Field(
        ...,
        description="The complete, fully edited document in Markdown format. This should be production-ready with all corrections and improvements applied inline."
    )