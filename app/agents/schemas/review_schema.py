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


class DimensionScore(BaseModel):
    """Dimension score object"""

    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Score for this dimension (0-100)"
    )

    assessment: Literal["excellent", "good", "fair", "poor"] = Field(
        ...,
        description="excellent=90+, good=75-89, fair=60-74, poor=<60"
    )


class Issue(BaseModel):
    """Individual issue found in the chapter"""

    dimension: Literal[
        "content_coverage",
        "content_depth",
        "structure_logic",
        "language_quality",
        "format",
        "length"
    ] = Field(
        ...,
        description="The dimension this issue belongs to"
    )

    severity: Literal["critical", "major", "minor"] = Field(
        ...,
        description="critical=must fix, major=recommended, minor=optional"
    )

    location: str = Field(
        ...,
        description="Precise location (e.g., 'Paragraph 3', 'Section 2.1')"
    )

    problem: str = Field(
        ...,
        description="Specific issue description. Be concrete, not vague"
    )

    suggestion: str = Field(
        ...,
        description="Improvement suggestion. Provide direction, don't rewrite"
    )


class ChapterReviewResult(BaseModel):
    """Chapter review result with structured output"""

    overall_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall quality score. 85+=excellent, 75-84=good, 60-74=acceptable, <60=needs revision"
    )

    dimensions: Dict[str, DimensionScore] = Field(
        ...,
        description="Scores for each dimension. Must include all 6: content_coverage, content_depth, structure_logic, language_quality, format, length"
    )

    issues: List[Issue] = Field(
        default_factory=list,
        description="Specific issues found, sorted by severity. Each linked to a dimension. Aim for <5 critical/major, <10 minor"
    )

    summary: str = Field(
        ...,
        description="2-3 sentence summary balancing strengths and weaknesses"
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