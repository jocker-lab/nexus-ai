# -*- coding: utf-8 -*-
"""
@File    :   document_summary_schema.py
@Time    :   2025/11/27
@Desc    :   文档摘要 Schema - 用于向量化存储前的结构化提取
"""

from pydantic import BaseModel, Field


class DocumentSummary(BaseModel):
    """
    文档摘要结构化输出

    用于从生成的完整文档中提取关键信息，
    title + summary 拼接后向量化存入 Milvus
    """

    title: str = Field(
        ...,
        description=(
            "文档标题，应准确概括文档主题和内容。"
            "例如：'中原银行2025年财务分析报告'、'AI芯片行业深度研究'"
        )
    )

    summary: str = Field(
        ...,
        description=(
            "文档内容的概要总结，200-300字。"
            "应涵盖：文档主题、核心观点、主要结论或发现。"
            "用于向量化后进行语义检索，需要包含足够的语义信息。"
        )
    )
