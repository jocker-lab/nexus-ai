"""
Chapter Writer - 基于 Agent 的智能写作系统（支持绘图）
"""
from typing import Dict, Any
from loguru import logger
from langchain.agents import create_agent
from app.agents.core.publisher.subgraphs.section_writer.state import ChapterState
from app.agents.tools.generation.chart_generation import generate_chart
from app.agents.prompts.template import render_prompt_template
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage


async def chapter_content_writer(state: ChapterState) -> Dict[str, Any]:
    chapter_id = state["chapter_id"]
    chapter_title = state["chapter_outline"].title

    # ===== 1. 开始写作章节（关键节点，建议用 info 保留在生产日志中）=====
    logger.info(f"[ChapterWriter] Chapter {chapter_id} | 开始写作章节：《{chapter_title}》")

    llm = init_chat_model("deepseek:deepseek-chat", temperature=0.8)

    # ===== 2. 加载 Prompt 模板（debug 级别，可过滤）=====
    logger.debug(f"[ChapterWriter] Chapter {chapter_id} | 渲染 System Prompt（语气: {state['document_outline'].writing_tone}, "
                 f"风格: {state['document_outline'].writing_style}, 语言: {state['document_outline'].language}）")

    system_prompt = render_prompt_template(
        "publisher_prompts/chapter_writing/chapter_writer_system",
        {
            "writer_role": state["writer_role"],
            "writer_profile": state["writer_profile"],
            "writing_principles": state["writing_principles"],
            "writing_tone": state["document_outline"].writing_tone,
            "writing_style": state["document_outline"].writing_style,
            "locale": state["document_outline"].language,
        }
    )
    user_messages = render_prompt_template(
        "publisher_prompts/chapter_writing/chapter_writer_task",
        state
    )

    # ===== 3. 创建 Agent（debug）=====
    logger.debug(f"[ChapterWriter] Chapter {chapter_id} | 创建写作 Agent（包含 generate_chart 工具）")

    agent = create_agent(model=llm, tools=[generate_chart], system_prompt=system_prompt)

    try:
        logger.info(f"[ChapterWriter] Chapter {chapter_id} | Agent 开始创作（带图表）...")

        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_messages}]},
            config={"recursion_limit": 50}
        )

        # 提取最后一条有效的 AI 消息
        ai_messages = [m for m in response["messages"] if isinstance(m, AIMessage) and m.content]
        if not ai_messages:
            raise ValueError("Agent 未返回任何有效的内容消息")

        draft = ai_messages[-1].content.strip()

        # ===== 4. 写作成功统计（info 级别，关键指标）=====
        word_count = len(draft)
        chart_count = draft.count('![')  # Markdown 图片语法计数

        logger.success(  # loguru 自带的 success 级别，比 info 更醒目
            f"[ChapterWriter] Chapter {chapter_id} | 写作完成 | "
            f"字数: {word_count:,}（目标 {state['chapter_outline'].estimated_words:,}） | "
            f"图表数: {chart_count}"
        )

    except Exception as e:
        logger.error(f"[ChapterWriter] Chapter {chapter_id} | Agent 写作失败: {e}")
        logger.exception(e)  # 自动打印完整 traceback，便于排查

        draft = f"## {chapter_title}\n\n[ERROR] 章节内容生成失败：{str(e)}"

        word_count = len(draft)
        chart_count = 0

    # ===== 5. 返回前再次记录一次摘要（方便后续节点快速看到结果）=====
    logger.info(
        f"[ChapterWriter] Chapter {chapter_id} | 最终输出摘要 | "
        f"字数: {word_count:,} | 图表数: {chart_count} | 预览: {draft[:100].replace(chr(10), ' ')}..."
    )

    return {
        "draft": draft
    }




