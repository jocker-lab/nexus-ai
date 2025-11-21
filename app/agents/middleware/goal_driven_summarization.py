# -*- coding: utf-8 -*-
"""
@File    :   goal_driven_summarization.py
@Time    :   2025/11/21
@Author  :   Claude
@Version :   1.0
@Desc    :   Goal-Driven Summarization Middleware - 基于研究目标的智能总结
"""

from typing import Any, cast
from collections.abc import Callable, Iterable

from langchain_core.messages import AnyMessage, RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.runtime import Runtime

from langchain.agents.middleware.summarization import (
    SummarizationMiddleware,
    TokenCounter,
    count_tokens_approximately,
)
from langchain.agents.middleware.types import AgentState
from langchain.chat_models import BaseChatModel


# Goal-Driven Summary Prompt
GOAL_DRIVEN_SUMMARY_PROMPT = """<role>
Goal-Driven Context Extraction Assistant
</role>

<current_research_objective>
The agent is currently working on the following research task:

**Chapter Title**: {chapter_title}

**Research Objective**: {chapter_description}

**Content Requirements**: {content_requirements}

**Subsections to Cover**:
{subsections}

</current_research_objective>

<primary_task>
Summarize the conversation history below, but ONLY preserve information that is directly relevant to the research objective above.
</primary_task>

<critical_instructions>
1. **Relevance-First Principle**:
   - If a message contains 90% irrelevant content and 10% relevant content, extract ONLY the 10%
   - Even if relevant content is a single sentence buried in a long webpage, it MUST be preserved
   - Irrelevant content should be discarded, even if it dominates the text volume
   - Example: If researching "AI software", discard hardware specs/pricing; if researching "market size", discard product features

2. **Explicit Negative Results**:
   - If a search returned ZERO relevant information, state: "已检查 [来源]，未找到相关信息"
   - This prevents the agent from repeating failed searches
   - But if there is PARTIAL information, extract and preserve it

3. **Preserve Critical Elements**:
   - Task progress markers (已完成/进行中/待完成)
   - Specific data points (numbers, percentages, dates, statistics)
   - Data sources and citations (Gartner, IDC, research institutions)
   - Key findings that match content requirements

4. **Consolidate Redundancy**:
   - If multiple searches found the same fact, mention it once
   - Combine related findings under the same topic
   - Remove process descriptions (e.g., "I will now search for...")

5. **What to DISCARD**:
   - Marketing fluff without factual content
   - Off-topic descriptions (e.g., product specs when researching market trends)
   - Background information not requested in content requirements
   - Duplicated information from multiple sources

</critical_instructions>

<output_requirements>
- **Language**: Use Chinese (中文) for the summary
- **Format**: Use structured bullet points organized by subsection or topic
- **Style**: Concise but preserve ALL goal-relevant facts
- **Structure Example**:
  ```
  ## 研究进度总结

  ### [子章节1标题]
  - ✓ 已完成：[具体发现]
    - 数据来源：[来源]
    - 关键数据：[具体数字]
  - ⚠️ 已检查但未找到：[尝试过的查询]

  ### [子章节2标题]
  - 🔄 进行中：[当前发现]
  ```
</output_requirements>

<examples>
Example 1 - Tesla FSD Case:
Research Goal: "Tesla FSD自动驾驶软件版本信息"
Tool Output: "[90% content about Model 3 interior, pricing, materials]... The vehicle is equipped with FSD V12.3 software, supporting city street navigation and automatic lane changes..."
✓ Correct Summary: "Tesla FSD V12.3版本：支持城市道路导航和自动变道功能"
✗ Wrong Summary: "Tesla Model 3价格为XX万元，采用XX材料，空间宽敞..." (irrelevant!)

Example 2 - Market Size Research:
Research Goal: "2024年全球AI市场规模数据"
Tool Output: "Artificial intelligence is transforming industries... According to Gartner, the global AI market reached $200 billion in 2024, growing at 35% YoY... Many startups are entering this space..."
✓ Correct Summary: "2024年全球AI市场规模：2000亿美元（来源：Gartner），同比增长35%"
✗ Wrong Summary: "人工智能正在改变各行各业，许多初创公司进入该领域..." (too vague!)
</examples>

<messages_to_summarize>
{messages}
</messages_to_summarize>

请输出总结（必须使用中文）:"""


class GoalDrivenSummarizationMiddleware(SummarizationMiddleware):
    """
    Goal-Driven Summarization Middleware

    基于研究目标的智能总结中间件。与标准的SummarizationMiddleware不同，
    这个中间件会从state中提取研究目标信息，并在总结时明确告诉LLM应该
    保留哪些信息、丢弃哪些信息。

    核心改进：
    1. 从chapter_outline提取研究目标
    2. 使用goal-driven prompt模板
    3. 保留与目标相关的信息，即使篇幅很短
    4. 丢弃与目标无关的信息，即使篇幅很大
    """

    def __init__(
        self,
        model: str | BaseChatModel,
        max_tokens_before_summary: int | None = None,
        messages_to_keep: int = 3,
        token_counter: TokenCounter = count_tokens_approximately,
        goal_extractor: Callable[[AgentState], dict[str, str]] | None = None,
    ) -> None:
        """
        初始化Goal-Driven Summarization Middleware

        Args:
            model: LLM模型
            max_tokens_before_summary: 触发总结的token阈值
            messages_to_keep: 总结后保留的最近消息数
            token_counter: Token计数函数
            goal_extractor: 自定义goal提取函数（可选）
        """
        # 使用goal-driven prompt初始化父类
        super().__init__(
            model=model,
            max_tokens_before_summary=max_tokens_before_summary,
            messages_to_keep=messages_to_keep,
            token_counter=token_counter,
            summary_prompt=GOAL_DRIVEN_SUMMARY_PROMPT,
        )

        self.goal_extractor = goal_extractor or self._default_goal_extractor

    def _default_goal_extractor(self, state: AgentState) -> dict[str, str]:
        """
        从state中提取研究目标信息

        提取优先级：
        1. chapter_outline (最优先，包含完整的研究目标)
        2. system message (次优先，包含任务描述)
        3. 默认值 (兜底)

        Returns:
            包含以下key的字典：
            - chapter_title: 章节标题
            - chapter_description: 研究目标描述
            - content_requirements: 内容需求
            - subsections: 子章节列表
        """
        # 尝试从chapter_outline提取
        if "chapter_outline" in state:
            chapter = state["chapter_outline"]

            # 构建subsections描述
            subsections_text = ""
            if hasattr(chapter, "subsections") and chapter.subsections:
                for i, subsec in enumerate(chapter.subsections, 1):
                    subsections_text += f"{i}. {subsec.sub_section_title}\n"
                    subsections_text += f"   - 描述: {subsec.description}\n"
                    if hasattr(subsec, "writing_guidance"):
                        subsections_text += f"   - 写作指导: {subsec.writing_guidance}\n"
            else:
                subsections_text = "暂无子章节划分"

            return {
                "chapter_title": getattr(chapter, "title", "未指定章节标题"),
                "chapter_description": getattr(chapter, "description", "未指定研究目标"),
                "content_requirements": getattr(chapter, "content_requirements", "未指定内容需求"),
                "subsections": subsections_text,
            }

        # 尝试从document_outline提取（如果存在）
        if "document_outline" in state:
            doc = state["document_outline"]
            return {
                "chapter_title": getattr(doc, "title", "研究任务"),
                "chapter_description": getattr(doc, "writing_purpose", "完成用户指定的研究任务"),
                "content_requirements": f"目标受众: {getattr(doc, 'target_audience', '未指定')}",
                "subsections": "参考文档整体结构",
            }

        # 尝试从messages提取（system prompt）
        messages = state.get("messages", [])
        if messages and hasattr(messages[0], "content"):
            system_content = str(messages[0].content)[:300]  # 只取前300字符
            return {
                "chapter_title": "当前研究任务",
                "chapter_description": system_content,
                "content_requirements": "请根据上下文确定",
                "subsections": "暂无明确划分",
            }

        # 默认兜底值
        return {
            "chapter_title": "研究任务",
            "chapter_description": "完成用户指定的信息收集和研究工作",
            "content_requirements": "收集相关数据和信息",
            "subsections": "根据研究进展动态调整",
        }

    def _create_summary(self, messages_to_summarize: list[AnyMessage], state: AgentState) -> str:
        """
        生成goal-driven summary

        重写父类方法以注入goal信息

        Args:
            messages_to_summarize: 需要总结的消息列表
            state: 当前agent state（用于提取goal）

        Returns:
            生成的总结文本
        """
        if not messages_to_summarize:
            return "暂无历史对话记录。"

        # 提取当前研究目标
        goal_context = self.goal_extractor(state)

        trimmed_messages = self._trim_messages_for_summary(messages_to_summarize)
        if not trimmed_messages:
            return "对话历史过长，无法生成总结。"

        try:
            # 使用goal-driven prompt（包含goal和messages参数）
            prompt = self.summary_prompt.format(
                messages=trimmed_messages,
                chapter_title=goal_context["chapter_title"],
                chapter_description=goal_context["chapter_description"],
                content_requirements=goal_context["content_requirements"],
                subsections=goal_context["subsections"],
            )

            response = self.model.invoke(prompt)
            summary = cast("str", response.content).strip()

            # 添加调试日志
            print(f"[GoalDrivenSummarization] 📋 Research Goal: {goal_context['chapter_title']}")
            print(f"[GoalDrivenSummarization] ✅ Summary generated: {len(summary)} chars")

            return summary

        except Exception as e:
            print(f"[GoalDrivenSummarization] ❌ Error: {e}")
            return f"总结生成失败: {e!s}"

    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """
        在模型调用前检查token并触发总结

        重写父类方法以传入state给_create_summary
        """
        messages = state["messages"]
        self._ensure_message_ids(messages)

        total_tokens = self.token_counter(messages)

        print(f"[GoalDrivenSummarization] 📊 Current tokens: {total_tokens}/{self.max_tokens_before_summary}")

        # 未达到阈值，不触发总结
        if (
            self.max_tokens_before_summary is not None
            and total_tokens < self.max_tokens_before_summary
        ):
            return None

        # 寻找安全的切分点
        cutoff_index = self._find_safe_cutoff(messages)

        if cutoff_index <= 0:
            print(f"[GoalDrivenSummarization] ⚠️ Token limit reached but no safe cutoff found")
            return None

        messages_to_summarize, preserved_messages = self._partition_messages(messages, cutoff_index)

        print(f"[GoalDrivenSummarization] 🔄 TRIGGERING GOAL-DRIVEN SUMMARIZATION:")
        print(f"  - Summarizing {len(messages_to_summarize)} messages")
        print(f"  - Preserving {len(preserved_messages)} recent messages")

        # 传入state以提取goal
        summary = self._create_summary(messages_to_summarize, state)

        print(f"  - Summary preview: {summary[:200]}...")

        new_messages = self._build_new_messages(summary)

        return {
            "messages": [
                RemoveMessage(id=REMOVE_ALL_MESSAGES),
                *new_messages,
                *preserved_messages,
            ]
        }
