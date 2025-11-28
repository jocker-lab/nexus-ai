# -*- coding: utf-8 -*-
"""
@File    :   template_outline_schema.py
@Time    :   2025/11/28
@Desc    :   模版大纲 Schema - 用于从用户上传文件中提取模版结构
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class TemplateSection(BaseModel):
    """模版章节结构"""

    title: str = Field(
        ...,
        description="章节标题，如：'公司概况'、'经营业绩'、'风险管理'"
    )

    description: str = Field(
        ...,
        description=(
            "该章节的目的和内容范围，说明这个章节要写什么。"
            "例如：'介绍公司基本情况，包括发展历程、组织架构和核心业务'"
        )
    )

    estimated_words: int = Field(
        default=500,
        description="该章节的建议字数"
    )

    key_points: List[str] = Field(
        default_factory=list,
        description=(
            "该章节应覆盖的关键要点列表。"
            "例如：['公司简介', '发展历程', '组织架构', '核心业务']"
        )
    )


class TemplateOutline(BaseModel):
    """
    模版大纲结构化输出

    用于从用户上传的文件中提取模版结构，
    存入向量库供 Planner 检索和参考
    """

    # ========== 基础信息（检索用）==========
    title: str = Field(
        ...,
        description=(
            "模版名称，准确概括模版类型。"
            "例如：'银行年度报告模版'、'行业研究报告模版'、'产品需求文档模版'"
        )
    )

    summary: str = Field(
        ...,
        description=(
            "模版简介，200-300字。"
            "描述该模版的用途、适用场景和主要特点。"
            "用于向量化检索，需要包含足够的语义信息。"
        )
    )

    category: str = Field(
        ...,
        description=(
            "模版分类。"
            "例如：'年度报告'、'行业研究'、'技术文档'、'商业计划书'、'产品文档'"
        )
    )

    # ========== 风格规范 ==========
    writing_style: Literal[
        "academic",      # 学术论文
        "business",      # 商业报告
        "technical",     # 技术文档
        "journalistic",  # 新闻报道
        "casual"         # 非正式
    ] = Field(
        default="business",
        description="写作风格"
    )

    writing_tone: Literal[
        "neutral",       # 客观中立
        "authoritative", # 权威专业
        "enthusiastic",  # 积极正面
        "critical",      # 批判分析
        "empathetic"     # 共情理解
    ] = Field(
        default="neutral",
        description="写作语气"
    )

    target_audience: str = Field(
        ...,
        description=(
            "目标读者群体。"
            "例如：'公司管理层和投资者'、'技术开发人员'、'行业分析师'"
        )
    )

    # ========== 结构信息 ==========
    sections: List[TemplateSection] = Field(
        ...,
        description="模版的章节结构列表"
    )

    estimated_total_words: int = Field(
        default=5000,
        description="模版建议的总字数"
    )

    # ========== 可选信息 ==========
    special_requirements: Optional[str] = Field(
        None,
        description=(
            "特殊要求或注意事项。"
            "例如：'需要包含风险披露章节'、'必须有数据图表支撑'"
        )
    )
