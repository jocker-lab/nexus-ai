# -*- coding: utf-8 -*-
"""
@File    :   template_outline_schema.py
@Time    :   2025/12/03
@Desc    :   模版大纲提取 Schema - LLM 结构化输出用
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SectionInfo(BaseModel):
    """章节信息"""
    title: str = Field(..., description="章节标题")
    description: str = Field("", description="章节描述/写作指导")
    estimated_percentage: float = Field(0, description="预估占比(%)")
    key_points: List[str] = Field(default_factory=list, description="关键要点")


class TemplateOutline(BaseModel):
    """
    模版大纲 - LLM 结构化输出

    用于 LangChain with_structured_output() 调用，
    从文档内容中提取写作模版的结构信息。
    """
    title: str = Field(..., description="模版标题")
    summary: str = Field(..., description="模版摘要（50-100字描述模版用途）")
    category: str = Field(..., description="分类（如：市场分析、信用评级、行业研究）")
    writing_style: str = Field(
        "business",
        description="写作风格（academic/business/technical/creative/journalistic）"
    )
    writing_tone: str = Field(
        "neutral",
        description="写作语气（formal/neutral/casual/professional/persuasive）"
    )
    target_audience: Optional[str] = Field(None, description="目标受众")
    sections: List[SectionInfo] = Field(default_factory=list, description="章节列表")
    special_requirements: Optional[str] = Field(None, description="特殊要求")
