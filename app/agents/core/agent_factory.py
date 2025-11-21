# -*- coding: utf-8 -*-
"""
@File    :   agent_factory.py
@Time    :   2025/11/21
@Author  :   Claude
@Version :   1.0
@Desc    :   Custom Agent Factory with Goal-Driven Summarization
"""

from collections.abc import Callable, Sequence
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware, InterruptOnConfig, TodoListMiddleware
from langchain.agents.middleware.types import AgentMiddleware
from langchain.agents.structured_output import ResponseFormat
from langchain_anthropic import ChatAnthropic
from langchain_anthropic.middleware import AnthropicPromptCachingMiddleware
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.cache.base import BaseCache
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore
from langgraph.types import Checkpointer

from deepagents.backends.protocol import BackendFactory, BackendProtocol
from deepagents.middleware.filesystem import FilesystemMiddleware
from deepagents.middleware.patch_tool_calls import PatchToolCallsMiddleware
from deepagents.middleware.subagents import CompiledSubAgent, SubAgent, SubAgentMiddleware

# 导入我们的Goal-Driven Summarization
from app.agents.middleware.goal_driven_summarization import GoalDrivenSummarizationMiddleware


BASE_AGENT_PROMPT = "In order to complete the objective that the user asks of you, you have access to a number of standard tools."


def get_default_model() -> ChatAnthropic:
    """Get the default model for deep agents."""
    return ChatAnthropic(
        model_name="claude-sonnet-4-5-20250929",
        max_tokens=20000,
    )


def create_goal_driven_deep_agent(
    model: str | BaseChatModel | None = None,
    tools: Sequence[BaseTool | Callable | dict[str, Any]] | None = None,
    *,
    system_prompt: str | None = None,
    middleware: Sequence[AgentMiddleware] = (),
    subagents: list[SubAgent | CompiledSubAgent] | None = None,
    response_format: ResponseFormat | None = None,
    context_schema: type[Any] | None = None,
    checkpointer: Checkpointer | None = None,
    store: BaseStore | None = None,
    backend: BackendProtocol | BackendFactory | None = None,
    interrupt_on: dict[str, bool | InterruptOnConfig] | None = None,
    debug: bool = False,
    name: str | None = None,
    cache: BaseCache | None = None,
    # Goal-Driven Summarization 参数
    use_goal_driven_summarization: bool = True,
    max_tokens_before_summary: int = 15000,
    messages_to_keep: int = 3,
) -> CompiledStateGraph:
    """
    Create a deep agent with Goal-Driven Summarization.

    这是deepagents.create_deep_agent的增强版本，使用Goal-Driven Summarization
    替代标准的SummarizationMiddleware。

    Args:
        model: The model to use. Defaults to Claude Sonnet 4.
        tools: The tools the agent should have access to.
        system_prompt: The additional instructions the agent should have.
        middleware: Additional middleware to apply after standard middleware.
        subagents: The subagents to use.
        response_format: A structured output response format.
        context_schema: The schema of the deep agent.
        checkpointer: Optional checkpointer for persisting agent state.
        store: Optional store for persistent storage.
        backend: Optional backend for file storage and execution.
        interrupt_on: Optional interrupt configs.
        debug: Whether to enable debug mode.
        name: The name of the agent.
        cache: The cache to use for the agent.
        use_goal_driven_summarization: 是否使用Goal-Driven Summarization（默认True）
        max_tokens_before_summary: 触发总结的token阈值（默认15000）
        messages_to_keep: 总结后保留的最近消息数（默认3）

    Returns:
        A configured deep agent with goal-driven summarization.
    """
    if model is None:
        model = get_default_model()

    # 选择Summarization中间件
    if use_goal_driven_summarization:
        summarization_middleware = GoalDrivenSummarizationMiddleware(
            model=model,
            max_tokens_before_summary=max_tokens_before_summary,
            messages_to_keep=messages_to_keep,
        )
        print(f"[AgentFactory] ✅ Using Goal-Driven Summarization (threshold={max_tokens_before_summary})")
    else:
        # 如果不使用goal-driven，回退到标准版本
        from langchain.agents.middleware.summarization import SummarizationMiddleware
        summarization_middleware = SummarizationMiddleware(
            model=model,
            max_tokens_before_summary=max_tokens_before_summary,
            messages_to_keep=messages_to_keep,
        )
        print(f"[AgentFactory] ⚠️  Using Standard Summarization (threshold={max_tokens_before_summary})")

    # 构建middleware stack
    deepagent_middleware = [
        TodoListMiddleware(),
        FilesystemMiddleware(backend=backend),
        SubAgentMiddleware(
            default_model=model,
            default_tools=tools,
            subagents=subagents if subagents is not None else [],
            default_middleware=[
                TodoListMiddleware(),
                FilesystemMiddleware(backend=backend),
                # SubAgent也使用同样的summarization策略
                GoalDrivenSummarizationMiddleware(
                    model=model,
                    max_tokens_before_summary=max_tokens_before_summary,
                    messages_to_keep=messages_to_keep,
                ) if use_goal_driven_summarization else SummarizationMiddleware(
                    model=model,
                    max_tokens_before_summary=max_tokens_before_summary,
                    messages_to_keep=messages_to_keep,
                ),
                AnthropicPromptCachingMiddleware(unsupported_model_behavior="ignore"),
                PatchToolCallsMiddleware(),
            ],
            default_interrupt_on=interrupt_on,
            general_purpose_agent=True,
        ),
        # 主Agent的summarization middleware
        summarization_middleware,
        AnthropicPromptCachingMiddleware(unsupported_model_behavior="ignore"),
        PatchToolCallsMiddleware(),
    ]

    # 添加用户自定义middleware
    if middleware:
        deepagent_middleware.extend(middleware)

    # 添加Human-in-the-loop
    if interrupt_on is not None:
        deepagent_middleware.append(HumanInTheLoopMiddleware(interrupt_on=interrupt_on))

    return create_agent(
        model,
        system_prompt=system_prompt + "\n\n" + BASE_AGENT_PROMPT if system_prompt else BASE_AGENT_PROMPT,
        tools=tools,
        middleware=deepagent_middleware,
        response_format=response_format,
        context_schema=context_schema,
        checkpointer=checkpointer,
        store=store,
        debug=debug,
        name=name,
        cache=cache,
    ).with_config({"recursion_limit": 1000})
