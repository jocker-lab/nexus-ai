"""
Chapter Researcher - 为章节搜索素材
"""
from loguru import logger
from typing import Dict, Any
from app.agents.core.publisher.subgraphs.chapter_writing.state import ChapterState
from app.agents.prompts.template import apply_prompt_template
from app.agents.core.publisher.subgraphs.research.agent import run_research_subgraph
from app.agents.schemas.research_schema import SearchQueryList
from langchain.chat_models import init_chat_model



async def chapter_researcher(state: ChapterState) -> Dict[str, Any]:

    chapter_id = state["chapter_id"]
    chapter_title = state["chapter_outline"].title

    logger.info(f"  🔍 [Chapter {chapter_id}] Researcher: 开始研究...")

    # === 1. 生成搜索查询 ===
    llm = init_chat_model("deepseek:deepseek-chat")

    try:
        llm_with_structure = llm.with_structured_output(SearchQueryList)

        # 使用 apply_prompt_template 加载 prompt
        messages = apply_prompt_template(
            "chapter_writing/research_query_generation",
            {
                "chapter_title": chapter_title,
                "chapter_outline": state["chapter_outline"],
            }
        )
        query_prompt = messages[0].content

        query_obj = llm_with_structure.invoke(query_prompt)

        queries = query_obj.query

        logger.info(f"    ↳ 生成了 {len(queries)} 个查询")

    except Exception as e:
        logger.warning(f"    ⚠️  查询生成失败: {e}")
        queries = [chapter_title]

    # === 2. 调用独立的 Research Subgraph ===
    logger.info(f"    ↳ 调用 Research Subgraph 执行并行研究...")

    try:
        # 获取章节优先级
        writing_priority = state["chapter_outline"].writing_priority if hasattr(state["chapter_outline"], "writing_priority") else "normal"

        # 执行并行研究
        research_results = await run_research_subgraph(
            topics=queries[:4],
            need_search=True,
            language="zh-CN",
            writing_priority=writing_priority
        )

        logger.success(f"    ✓ 研究完成 ({len(research_results)} 字符)\n")

    except Exception as e:
        logger.error(f"    ⚠️  研究失败: {e}\n", exception=e)
        import traceback
        traceback.print_exc()
        research_results = f"Research failed for: {chapter_title}"

    # === 3. 返回结果 ===
    return {
        "synthesized_materials": research_results,
    }