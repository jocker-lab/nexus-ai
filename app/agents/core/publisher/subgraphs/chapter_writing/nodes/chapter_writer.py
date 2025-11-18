"""
Chapter Writer - 基于 Agent 的智能写作系统（支持绘图）
"""
from typing import Dict, Any
from loguru import logger
from langchain.agents import create_agent
from app.agents.core.publisher.subgraphs.chapter_writing.state import ChapterState
from app.agents.tools.generation.chart_generation import generate_chart
from app.agents.tools.thinking.thinking_tools import think, criticize, plan
from app.agents.prompts.template import apply_prompt_template, render_prompt_template
from langchain.chat_models import init_chat_model


async def chapter_content_writer(state: ChapterState) -> Dict[str, Any]:
    chapter_id = state["chapter_id"]
    chapter_title = state["chapter_outline"].title

    # === 检测场景：初始写作 vs 修订 ===
    revision_count = state.get("revision_count", 0)

    # ✅ 修复：通过 revision_count 判断是否是修订模式
    # 如果 revision_count > 0，说明已经经过至少一次审查，现在是修订模式
    is_revision = revision_count > 0

    # ✅ document_outline 由 dispatcher 保证传入，使用直接访问
    outline = state["document_outline"]

    if is_revision:
        logger.info(f"  🔄 [Chapter {chapter_id}] Writer: 执行修订 (第 {revision_count} 次修订后的再写作)...")
    else:
        logger.info(f"  ✍️  [Chapter {chapter_id}] Writer: 开始智能写作（支持绘图）...")

    # === 1. 初始化 LLM ===

    llm = init_chat_model("deepseek:deepseek-chat")
    # === 2. 加载 System Prompt ===
    # apply_prompt_template 返回 List[SystemMessage]，我们需要提取 content
    system_messages = render_prompt_template(
        "chapter_writing/chapter_writer_system",
        {
            "writing_tone": outline.writing_tone,
            "writing_style": outline.writing_style,
            "locale": outline.language,
        }
    )
    print("========" * 10)
    print(system_messages)
    print("system_messages" * 10)
    # === 3. 创建 Agent ===
    agent = create_agent(
        model=llm,
        tools=[generate_chart, think, criticize],
        system_prompt=system_messages
    )

    # === 4. 准备用户输入 ===
    # 使用 Jinja2 模板生成任务描述
    user_messages = render_prompt_template(
        "chapter_writing/chapter_writer_task",
        state
    )

    print("========" * 10)
    print(user_messages)
    print("========" * 10)
    # 记录 prompt（Agent 的用户输入）

    try:
        logger.info(f"    ↳ 启动 Agent（带绘图能力）...")

        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_messages}]},
            config={
                "recursion_limit": 50,  # 允许多次工具调用
            }
        )

        # 提取最终内容（最后一条 AI 消息）
        from langchain_core.messages import AIMessage
        ai_messages = [m for m in response["messages"] if isinstance(m, AIMessage) and m.content]

        if ai_messages:
            draft = ai_messages[-1].content.strip()

        else:
            raise ValueError("Agent 未返回有效内容")

    except Exception as e:
        logger.error(f"    ❌ Agent 写作失败: {e}\n", exception=e)
        import traceback
        traceback.print_exc()

        # ✅ 安全获取 draft_content，避免 KeyError
        if is_revision:
            draft = state.get("draft_content", f"## {chapter_title}\n\nError: Missing previous draft")
        else:
            draft = f"## {chapter_title}\n\nError: Failed to generate content for {chapter_title}"

    # === 6. 后处理 ===
    word_count = len(draft)

    logger.info(f"    ↳ 字数: {word_count} (目标: {state['target_word_count']})")
    logger.info(f"    ↳ 图表数: {draft.count('![')}")  # 统计图表数量
    logger.info(f"    ↳ 当前修订次数: {revision_count}\n")

    # === 返回更新 ===
    # 注意：
    # 1. revision_count 由 reviewer 节点管理，writer 不更新
    # 2. revision_history 由 reviewer 节点管理，writer 不更新
    return {
        "draft_content": draft,
        "word_count": word_count,
        # ✅ 不更新 revision_count，让 reviewer 来更新
    }




