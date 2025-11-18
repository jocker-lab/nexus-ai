# -*- coding: utf-8 -*-
"""
@File    :   document_outline_schema.py
@Time    :   2025/11/14 15:15
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


# 定义 SubSection 模型（子章节）
class SubSection(BaseModel):
    """
    Subsection model for detailed content organization within parent sections.
    Represents a focused content division supporting the parent section's objectives.
    """

    sub_section_title: str = Field(
        ...,
        description=(
            "Subsection heading that clearly identifies the specific focus area. "
            "Should be more granular than parent section title, concise (3-8 words), and descriptive. "
            "Examples: 'Customer Acquisition Costs', 'Regulatory Compliance Challenges', 'Q4 Performance Metrics'. "
            "Avoid generic terms; be specific and directly indicate the subsection's core topic."
        )
    )

    description: Optional[str] = Field(
        None,
        description=(
            "Comprehensive overview explaining the subsection's purpose, goals, and core content within the document hierarchy. "
            "Should articulate: "
            "(1) **Why**: Rationale for this subsection's existence and its role in supporting the parent section, "
            "(2) **What**: Specific objective it aims to achieve (inform, persuade, analyze, compare, evaluate), "
            "(3) **Coverage**: High-level summary of topics, arguments, or narratives to be addressed. "
            "Provide sufficient detail to guide the author's tone, scope, and key messaging direction, "
            "while remaining concise to avoid redundancy with detailed content plans. "
            "Target length: 50-200 words. "
            "Example: 'Examines the cost structure of customer acquisition across digital and traditional channels, "
            "comparing CAC/LTV ratios to identify the most cost-effective marketing investments for scaling operations.'"
        )
    )

    writing_guidance: Optional[str] = Field(
        None,
        description=(
            "Specific content development instructions to ensure accurate direction, logical coherence, and effective execution. "
            "Must include: "
            "1. **Entry Angle**: Perspective or approach for content development "
            "(e.g., data-driven comparison, case study analysis, theoretical exposition, chronological narrative), "
            "2. **Argumentation Logic**: Structure for content progression and reasoning flow "
            "(e.g., macro-to-micro, phenomenon-to-root-cause, problem-solution, compare-contrast, thesis-evidence-conclusion), "
            "3. **Emphasis Points**: Specific viewpoints, data, or arguments requiring prominent treatment and detailed elaboration, "
            "4. **Writing Techniques**: Recommended methods to enhance clarity and impact "
            "(e.g., data visualization, case evidence, statistical analysis, analogical reasoning, expert citations), "
            "5. **Transitions**: Logical connectors establishing flow with preceding and following sections, "
            "ensuring smooth narrative continuity. "
            "Length requirement: 100-400 characters. "
            "Style: Imperative, specific, actionable, and directly executable by writers. "
            "Example: 'Adopt a comparative positioning strategy. Begin with 3-5 core metrics establishing horizontal benchmark framework. "
            "Follow data presentation → gap quantification → brief causal analysis three-part structure. "
            "Emphasize significant disadvantages using radar chart for multi-dimensional comparison visualization. "
            "Transition by identifying disadvantage areas discovered through benchmarking for deep diagnostic analysis in next chapter.'"
        )
    )

    estimated_word_count: Optional[int] = Field(
        None,
        description=(
            "Target word count for this subsection based on content depth and role within the overall document. "
            "Serves as a guideline to maintain balanced proportions across subsections. "
            "Typical ranges by subsection type: "
            "- Detailed analysis or core arguments: 400-800 words, "
            "- Supporting evidence or contextual information: 300-500 words, "
            "- Transitional or connecting sections: 200-400 words. "
            "Default range: 200-600 words if not otherwise specified. "
            "This count represents the subsection's standalone content contribution within its parent section's total word allocation."
        )
    )


# 定义 Section 模型（章节），支持嵌套
class Section(BaseModel):
    """
    Hierarchical section model supporting multi-level nesting for document structure.
    Represents a logical division of content with guidance for writing and research.
    """

    title: str = Field(
        ...,
        description=(
            "Section heading that clearly indicates content focus. "
            "Should be concise (3-10 words), descriptive, and aligned with document hierarchy. "
            "Examples: 'Market Analysis Overview', '3.2 Implementation Challenges', 'Conclusion'"
        )
    )

    description: str = Field(
        ...,
        description=(
            "High-level overview explaining the section's purpose, scope, and contribution to the document. "
            "Should address: (1) Why this section exists, (2) What it aims to achieve (inform/persuade/analyze), "
            "(3) Key topics or narratives covered. "
            "Keep concise (50-200 words) to avoid redundancy with key_points or subsections. "
            "Example: 'This section examines the regulatory landscape affecting fintech adoption, "
            "analyzing policy frameworks across three major markets to identify barriers and enablers.'"
        )
    )

    writing_guidance: Optional[str] = Field(
        None,
        description=(
            "Tactical instructions for content development, ensuring coherent narrative flow and appropriate depth. "
            "Should specify: "
            "1) **Approach**: Entry angle (e.g., data-driven comparison, case study analysis, theoretical framework) "
            "2) **Structure**: Argumentation logic (e.g., problem-solution, chronological, compare-contrast) "
            "3) **Emphasis**: Critical points requiring detailed treatment or special attention "
            "4) **Techniques**: Recommended methods (e.g., statistical evidence, expert citations, analogies) "
            "5) **Transitions**: How to connect with preceding/following sections "
            "Length: 100-400 characters. Style: Imperative, specific, actionable. "
            "Example: 'Open with quantitative benchmarking using 3-5 KPIs. Follow problem→impact→root cause structure. "
            "Emphasize performance gaps with radar chart visualization. Transition by identifying deficiency areas for next chapter's deep-dive.'"
        )
    )

    content_requirements: Optional[str] = Field(
        None,
        description=(
            "Specifications for research materials, data sources, and evidence needed to write this section. "
            "Include: "
            "- **Data needs**: Specific datasets, statistics, metrics (e.g., 'Q4 2024 market share data from IDC') "
            "- **Source criteria**: Authority level, recency requirements (e.g., 'peer-reviewed papers from 2020+') "
            "- **Evidence types**: Expert quotes, case studies, regulatory documents, technical specifications "
            "- **Quality standards**: Credibility thresholds, geographic scope, sample size minimums "
            "Example: 'Require: (1) FDA approval timelines 2018-2024 from official database, "
            "(2) 3-5 expert opinions from pharma executives, (3) cost-benefit analyses from academic journals (impact factor >3).'"
        )
    )

    visual_elements: Optional[bool] = Field(
        None,
        description=(
            "Whether this section requires charts, graphs, tables, diagrams, or other visual aids. "
            "Set to True if visual elements are needed to enhance comprehension, False otherwise. "
            "Examples of when to use: data comparisons, process flows, trend analysis, statistical results."
        )
    )

    estimated_words: int = Field(
        ...,
        description=(
            "Target word count for this section's main content (excluding subsection content if present). "
            "Used for proportional allocation and scope control. "
            "Guidelines: Introduction (200-400), Analysis sections (600-1200), Subsection components (300-600). "
            "For sections with subsections, count should reflect introductory/connecting text only."
        )
    )

    writing_priority: Literal["high", "medium", "low"] = Field(
        default="medium",
        description=(
            "Relative importance for resource allocation and writing effort. "
            "**High**: Core arguments, critical analysis, unique value proposition. "
            "**Medium**: Supporting sections, standard analysis, contextual information. "
            "**Low**: Supplementary content, optional deep-dives, tangential topics. "
            "Guides writers on depth expectations and review focus."
        )
    )

    subsections: List[SubSection] = Field(
        default_factory=list,
        description=(
            "Nested child sections for hierarchical content organization. "
            "Use when a section requires logical subdivision into distinct topics. "
            "Each subsection inherits context from parent but maintains independent scope. "
            "Maximum recommended nesting depth: 3-4 levels for readability. "
            "Empty list indicates leaf-level section with no further subdivision."
        )
    )


class DocumentOutline(BaseModel):
    """
    Comprehensive document outline schema for structured content generation.
    Supports multiple writing styles and formats including reports, articles,
    essays, and technical documentation.
    """

    title: str = Field(
        ...,
        description=(
            "Primary document title that concisely captures the core subject matter. "
            "Should be descriptive and engaging, typically 5-15 words. "
            "Examples: 'Comparative Analysis of US-China Economic Relations', "
            "'Introduction to Machine Learning Fundamentals'"
        )
    )

    language: str = Field(
        ...,
        description=(
            "Primary language for document composition. Use ISO 639-1 codes when possible "
            "(e.g., 'en' for English, 'zh' for Chinese) or full language names "
            "(e.g., 'English', 'Chinese', 'Spanish'). "
            "If unspecified by user, infer from query language or default to 'en'."
        )
    )

    target_audience: str = Field(
        ...,
        description=(
            "Intended readership profile that guides content depth, terminology, and assumptions. "
            "Specify expertise level, professional background, or demographic characteristics. "
            "Examples: 'Graduate students in economics', 'C-suite executives in tech industry', "
            "'General public with basic financial literacy', 'Software engineers with 3+ years experience'."
        )
    )

    writing_style: Literal[
        "academic",      # Scholarly research papers, dissertations
        "business",      # Corporate reports, proposals, white papers
        "creative",      # Literary works, storytelling, narrative essays
        "technical",     # Documentation, specifications, manuals
        "journalistic",  # News articles, feature stories, investigative pieces
        "casual"         # Blog posts, social media, informal communications
    ] = Field(
        default="business",
        description=(
            "Overarching stylistic framework that determines structural conventions, "
            "citation practices, and rhetorical approach. Each style has distinct "
            "expectations for evidence presentation, argumentation, and formatting."
        )
    )

    writing_tone: Literal[
        "neutral",        # Objective, unbiased presentation
        "enthusiastic",   # Positive, energetic, motivational
        "critical",       # Analytical, questioning, evaluative
        "empathetic",     # Understanding, compassionate, supportive
        "authoritative",  # Expert, confident, definitive
        "humorous"        # Light, entertaining, witty
    ] = Field(
        default="neutral",
        description=(
            "Emotional and attitudinal coloring that shapes word choice, sentence structure, "
            "and reader engagement. Tone should align with both content subject matter and "
            "target audience expectations."
        )
    )

    writing_purpose: str = Field(
        ...,
        description=(
            "Concise statement of the document's primary objective and intended impact. "
            "Should articulate what the reader will gain, understand, or be able to do after reading. "
            "Focus on value proposition rather than content description. "
            "Examples: 'To equip product managers with actionable frameworks for prioritization decisions', "
            "'To provide investors with comprehensive risk assessment of emerging markets'. "
            "Maximum length: 500 characters to maintain focus and clarity."
        ),
        max_length=500
    )

    key_themes: List[str] = Field(
        ...,
        description=(
            "Core thematic pillars or central arguments that structure the document's narrative arc. "
            "Each theme should represent a distinct conceptual thread that can anchor one or more sections. "
            "Requirements: "
            "1) Specific and actionable - not generic concepts (e.g., 'Impact of remote work on productivity metrics' "
            "rather than 'Remote work') "
            "2) Logically distinct yet complementary to other themes "
            "3) Directly derivable from the stated purpose "
            "4) Suitable as section-level organizing principles "
            "Optimal range: 3-7 themes for balanced scope and depth."
        )
    )

    estimated_total_words: int = Field(
        default=5000,
        ge=500,
        le=100000,
        description=(
            "Target word count for the complete document, excluding references and appendices. "
            "Used for scope planning and section allocation. "
            "Guidelines: Blog posts (500-2000), Articles (2000-5000), Reports (5000-15000), "
            "Academic papers (7000-12000), Books (50000+). "
            "Default: 5000 words if not specified by user."
        )
    )

    sections: List[Section] = Field(
        ...,
        description=(
            "Hierarchical outline of document structure with top-level sections and optional subsections. "
            "Each section should have: (1) Clear descriptive title, (2) Scope definition in description, "
            "(3) Proportional word allocation. Section word counts should sum to approximately total word count. "
            "Support nested structures for complex documents (e.g., chapters → sections → subsections)."
        )
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "title": "2025年度市场分析报告",
                "language": "Chinese",
                "target_audience": "公司管理层、投资者、市场分析师",
                "writing_style": "professional",
                "writing_tone": "authoritative",
                "writing_purpose": "为管理层提供全面的市场洞察和战略建议",
                "key_themes": ["市场趋势", "竞争分析", "风险评估", "发展建议"],
                "estimated_total_words": 8000,
                "sections": [
                    {
                        "section_title": "执行摘要",
                        "description": "提供报告核心发现和关键建议",
                        "key_points": ["核心发现", "关键数据", "主要建议"],
                        "writing_guidance": "简明扼要，突出重点，便于快速决策",
                        "need_chart": False,
                        "estimated_word_count": 800,
                        "subsections": []
                    }
                ]
            }]
        }
    )
