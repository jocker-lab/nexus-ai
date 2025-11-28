"""
Chapter Researcher - 为章节搜索素材
"""
from loguru import logger
from typing import Dict, Any, List
from app.agents.core.publisher.subgraphs.section_writer.state import ChapterState
from app.agents.prompts.template import apply_prompt_template
from app.agents.core.publisher.subgraphs.research.agent import run_research_subgraph
from app.agents.schemas.research_schema import SearchQueryList
from langchain.chat_models import init_chat_model

MAX_QUERIES_PER_CHAPTER = 5       # 最多并行多少个查询


async def chapter_researcher(state: ChapterState) -> Dict[str, Any]:

    chapter_id = state["chapter_id"]
    chapter_title = state["chapter_outline"].title

    logger.info(f"🔍 [Chapter {chapter_id}] Researcher 开始研究章节：《{chapter_title}》")
    # === 1. 生成搜索查询 ===
    llm = init_chat_model("deepseek:deepseek-chat")

    queries: List[str] = []
    try:
        llm_with_structure = llm.with_structured_output(SearchQueryList)

        # 使用 apply_prompt_template 加载 prompt
        messages = apply_prompt_template(
            "publisher_prompts/chapter_writing/research_query_generation",
            {
                "chapter_title": chapter_title,
                "chapter_outline": state["chapter_outline"],
            }
        )

        query_obj: SearchQueryList = llm_with_structure.invoke(messages)

        queries = query_obj.query

        logger.info(f"    ↳ 生成了 {len(queries)} 个查询")

    except Exception as e:
        logger.warning(f"⚠️ 查询生成失败，使用兜底查询: {e}")
        queries = [chapter_title]  # 永远不会让这一步直接崩

    try:
        logger.info(f"↳ 尝试调用 Research Subgraph（查询数：{len(queries)}）...")
        # 执行并行研究
        research_results = await run_research_subgraph(topics=queries[:MAX_QUERIES_PER_CHAPTER], need_search=True, language="zh-CN")

        total_chars = len(str(research_results))
        logger.success(f"✓ 研究成功！本次获取素材约 {total_chars:,} 字符")
        synthesized_materials = research_results

    except Exception as e:
        logger.error(f"    ⚠️  研究失败: {e}\n", exception=e)
        synthesized_materials = f"【无素材】章节《{chapter_title}》未能获取到研究素材，已使用兜底策略。"
    # === 3. 返回结果 ===
    return {
        # 关键：把本次用了哪些查询也带下去，后续任何节点都能看到、调试、审计
        "research_queries": queries,

        # 关键：永远返回 str，下游写作节点再也不用判断类型了
        "research_data": synthesized_materials or f"【无素材】章节《{chapter_title}》未能获取到研究素材，已使用兜底策略。",
    }