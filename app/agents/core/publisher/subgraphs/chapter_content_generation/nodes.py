"""
Chapter Content Generation Nodes - Iterative Chapter Generation Implementation
"""
import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from loguru import logger
from typing import Dict, Any, List
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel, Field
from langgraph.types import Send, Command

from app.agents.core.publisher.subgraphs.chapter_content_generation.state import (
    ChapterIterativeState,
)
from app.agents.prompts.template import render_prompt_template
from app.agents.tools.generation.chart_generation import generate_chart
from app.agents.tools.thinking.thinking_tools import think, criticize

load_dotenv()

# Prompt 模板路径前缀
PROMPT_PATH = "publisher_prompts/chapter_content_generation"

# 最大迭代次数限制（防止无限循环）
MAX_ITERATIONS = 3


# ============================================================
# Pydantic Schema for Structured Output
# ============================================================

class QueryList(BaseModel):
    """List of search queries"""
    queries: List[str] = Field(description="List of search queries (1-3)")


class DraftEvaluation(BaseModel):
    """Draft evaluation result"""
    is_satisfied: bool = Field(description="Whether the current draft is satisfactory (True if coverage >= 0.7)")
    coverage_score: float = Field(description="Coverage score (0-1)")
    follow_up_queries: List[str] = Field(default=[], description="Follow-up search queries to fill gaps. Empty list if satisfied.")


# ============================================================
# Node 1: Generate Initial Queries (只在第一轮执行)
# ============================================================

def generate_queries_node(state: ChapterIterativeState) -> Command:
    """
    Node 1: Generate initial search queries based on chapter outline

    只在第一轮执行，根据 chapter_outline 生成 3 个初始 queries

    Output: Command with Send list to search_node
    """
    chapter_id = state["chapter_id"]
    chapter_outline = state["chapter_outline"]
    chapter_title = chapter_outline.title
    chapter_description = getattr(chapter_outline, "description", "")
    content_requirements = getattr(chapter_outline, "content_requirements", "")
    writing_guidance = getattr(chapter_outline, "writing_guidance", "")

    llm = ChatDeepSeek(model="deepseek-chat", temperature=0)
    llm_with_structure = llm.with_structured_output(QueryList)

    logger.info(f"  🔍 [Chapter {chapter_id}] Generating initial search queries...")
    prompt = render_prompt_template(f"{PROMPT_PATH}/generate_queries_initial", {
        "chapter_title": chapter_title,
        "chapter_description": chapter_description,
        "content_requirements": content_requirements,
        "writing_guidance": writing_guidance,
    })

    try:
        result = llm_with_structure.invoke(prompt)
        queries = result.queries[:3]  # Ensure max 3 queries

        logger.info(f"    ✓ Generated {len(queries)} queries:")
        for i, query in enumerate(queries, 1):
            logger.info(f"      {i}. {query}")

        # Build Send list for parallel search
        send_list = [
            Send("search", {
                "chapter_id": chapter_id,
                "chapter_outline": chapter_outline,
                "search_query": query,
            })
            for query in queries
        ]

        logger.info(f"    ✓ Dispatching {len(send_list)} parallel searches...")

        return Command(goto=send_list)

    except Exception as e:
        logger.error(f"    ⚠️  Query generation failed: {e}")
        fallback_query = f"{chapter_title} {content_requirements}"
        logger.info(f"    ↳ Using fallback query: {fallback_query}")

        return Command(goto=[Send("search", {
            "chapter_id": chapter_id,
            "chapter_outline": chapter_outline,
            "search_query": fallback_query,
        })])


# ============================================================
# Node 2: Search (Pure Search Node)
# ============================================================

def search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 2: Pure search execution (supports parallel execution)

    Input: search_query (passed via Send)
    Output: search_results (list with single result, aggregated by operator.add)
    """
    chapter_id = state.get("chapter_id", "?")
    search_query = state.get("search_query", "")

    logger.info(f"  🔍 [Chapter {chapter_id}] Searching...")
    logger.info(f"    Query: {search_query}")

    try:
        from app.agents.tools.search.tavily_search import searcher
    except ImportError:
        logger.error("    ⚠️  Cannot import search tool")
        return {
            "search_results": [{
                "query": search_query,
                "content": f"Search tool unavailable. Placeholder content for: {search_query}"
            }]
        }

    try:
        search_content = searcher.invoke(search_query, max_results=5)
        logger.info(f"    ✓ Search completed ({len(search_content)} characters)")

        return {
            "search_results": [{
                "query": search_query,
                "content": search_content
            }]
        }

    except Exception as e:
        logger.error(f"    ⚠️  Search failed: {e}")
        return {
            "search_results": [{
                "query": search_query,
                "content": f"Search failed: {str(e)}. Query was: {search_query}"
            }]
        }


# ============================================================
# Node 3: Write/Refine Draft (Agent with Chart Generation)
# ============================================================

async def write_node(state: ChapterIterativeState) -> Dict[str, Any]:
    """
    Node 3: Write or refine draft using Agent with chart generation capability

    Input: search_results (list), draft, iteration, chapter_outline, writer context
    Output: updated draft, iteration+1, search_results=[] (清空为下轮准备)
    """
    chapter_id = state["chapter_id"]
    chapter_outline = state["chapter_outline"]
    chapter_title = chapter_outline.title
    iteration = state.get("iteration", 0)
    draft = state.get("draft", "")
    search_results_list = state.get("search_results", [])
    target_word_count = getattr(chapter_outline, "estimated_words", 800)

    description = getattr(chapter_outline, "description", "")
    content_requirements = getattr(chapter_outline, "content_requirements", "")
    writing_guidance = getattr(chapter_outline, "writing_guidance", "")
    visual_elements = getattr(chapter_outline, "visual_elements", False)

    # 获取写作上下文（从 section_writer 传入）
    document_outline = state.get("document_outline")
    writer_role = state.get("writer_role", "Expert Content Writer")
    writer_profile = state.get("writer_profile", "")
    writing_principles = state.get("writing_principles", [])

    # 从 document_outline 获取写作风格信息
    writing_tone = getattr(document_outline, "writing_tone", "") if document_outline else ""
    writing_style = getattr(document_outline, "writing_style", "") if document_outline else ""
    language = getattr(document_outline, "language", "Chinese") if document_outline else "Chinese"

    # ==================== 章节写作日志 ====================
    logger.info("")
    logger.info("=" * 80)
    logger.info(f"📝 [WRITE_NODE] Chapter {chapter_id}: {chapter_title}")
    logger.info("=" * 80)
    logger.info(f"  📋 Iteration: {iteration + 1}")
    logger.info(f"  👤 Writer: {writer_role}")
    logger.info(f"  📊 Chart generation: {'✅ Enabled' if visual_elements else '❌ Disabled'}")
    logger.info(f"  🎯 Target words: {target_word_count}")

    # Initialize LLM
    llm = init_chat_model("deepseek:deepseek-chat")

    # Format search results
    search_results_text = "\n\n---\n\n".join([
        f"**Query**: {r['query']}\n**Results**:\n{r['content']}"
        for r in search_results_list
    ]) if search_results_list else "No search results available."

    # 计算迭代状态
    revision_needed = iteration > 0

    # 构建统一的模板参数（包含所有模板可能需要的变量）
    template_params = {
        # 基础 state 字段
        "chapter_id": chapter_id,
        "chapter_outline": chapter_outline,
        "document_outline": document_outline,

        # 写作上下文
        "writer_role": writer_role,
        "writer_profile": writer_profile,
        "writing_principles": writing_principles,
        "writing_tone": writing_tone,
        "writing_style": writing_style,
        "language": language,

        # 内容参数
        "target_word_count": target_word_count,
        "search_results_text": search_results_text,
        "visual_elements": visual_elements,

        # 迭代控制参数
        "revision_needed": revision_needed,
        "draft": draft,  # 始终传递，模板根据 revision_needed 决定是否使用
    }

    # 统一使用一个系统提示和一个用户提示模板
    system_prompt = render_prompt_template(f"{PROMPT_PATH}/write_draft_system", template_params)
    user_prompt = render_prompt_template(f"{PROMPT_PATH}/write_draft_initial", template_params)

    # Create Agent with tools
    agent = create_agent(model=llm, tools=[generate_chart], system_prompt=system_prompt)

    try:
        logger.info("-" * 80)
        logger.info(f"📤 [PROMPT] Chapter {chapter_id}: {chapter_title}")
        logger.info("-" * 80)
        logger.info(f"  🔧 System Prompt ({len(system_prompt)} chars):")
        # 只打印前500字符，避免日志过长
        system_preview = system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt
        for line in system_preview.split('\n')[:10]:  # 只显示前10行
            logger.info(f"    | {line}")
        if len(system_prompt) > 500:
            logger.info(f"    | ... (truncated, total {len(system_prompt)} chars)")
        logger.info("")
        logger.info(f"  📝 User Prompt ({len(user_prompt)} chars):")
        user_preview = user_prompt[:500] + "..." if len(user_prompt) > 500 else user_prompt
        for line in user_preview.split('\n')[:10]:  # 只显示前10行
            logger.info(f"    | {line}")
        if len(user_prompt) > 500:
            logger.info(f"    | ... (truncated, total {len(user_prompt)} chars)")
        logger.info("-" * 80)
        logger.info(f"🚀 Starting Agent for Chapter {chapter_id}...")

        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_prompt}]},
            config={"recursion_limit": 50}
        )

        # Extract final content (last AI message)
        ai_messages = [m for m in response["messages"] if isinstance(m, AIMessage) and m.content]

        if ai_messages:
            new_draft = "\n\n".join(m.content.strip() for m in ai_messages)
        else:
            raise ValueError("Agent did not return valid content")


        logger.info("-" * 80)
        logger.info(f"📥 [RESULT] Chapter {chapter_id}: {chapter_title}")
        logger.info("-" * 80)
        logger.info(f"  ✅ Draft length: {len(new_draft)} characters")
        logger.info(f"  📊 Charts generated: {new_draft.count('![')}")
        # 显示结果预览
        logger.info(f"  📄 Content preview:")
        draft_preview = new_draft[:300] + "..." if len(new_draft) > 300 else new_draft
        for line in draft_preview.split('\n')[:8]:  # 只显示前8行
            logger.info(f"    | {line[:80]}")  # 每行最多80字符
        if len(new_draft) > 300:
            logger.info(f"    | ... (truncated, total {len(new_draft)} chars)")
        logger.info("=" * 80)
        logger.info("")

        # 完整内容输出（用于调试，可通过环境变量 LOG_FULL_DRAFT=true 控制）
        if os.getenv("LOG_FULL_DRAFT", "false").lower() == "true":
            logger.debug(f"[FULL_DRAFT] Chapter {chapter_id}: {chapter_title}\n{new_draft}")

        return {
            "draft": new_draft,
            "iteration": iteration + 1,
            "search_results": None  # 使用 None 触发 reducer 清空逻辑
        }

    except Exception as e:
        logger.error("")
        logger.error("=" * 80)
        logger.error(f"❌ [ERROR] Chapter {chapter_id}: {chapter_title}")
        logger.error("=" * 80)
        logger.error(f"  ⚠️ Writing failed: {e}")
        import traceback
        traceback.print_exc()
        fallback_draft = draft if draft else f"# {chapter_title}\n\nWriting failed: {str(e)}"
        return {
            "draft": fallback_draft,
            "iteration": iteration + 1,
            "search_results": None  # 使用 None 触发 reducer 清空逻辑
        }


# ============================================================
# Node 4: Evaluate Draft Quality
# ============================================================

def evaluate_node(state: ChapterIterativeState) -> Dict[str, Any]:
    """
    Node 4: Evaluate draft quality and generate follow-up queries if needed

    Input: draft, chapter_outline
    Output: is_satisfied, follow_up_queries (直接生成后续查询)
    """
    chapter_id = state["chapter_id"]
    chapter_outline = state["chapter_outline"]
    chapter_title = chapter_outline.title
    draft = state.get("draft", "")
    target_word_count = getattr(chapter_outline, "estimated_words", 800)

    chapter_description = getattr(chapter_outline, "description", "")
    writing_guidance = getattr(chapter_outline, "writing_guidance", "")
    content_requirements = getattr(chapter_outline, "content_requirements", "")

    logger.info(f"  📊 [Chapter {chapter_id}] Evaluating draft...")

    llm = init_chat_model("deepseek:deepseek-chat")
    llm_with_structure = llm.with_structured_output(DraftEvaluation)

    eval_prompt = render_prompt_template(f"{PROMPT_PATH}/evaluate_draft", {
        "chapter_title": chapter_title,
        "chapter_description": chapter_description,
        "writing_guidance": writing_guidance,
        "content_requirements": content_requirements,
        "target_word_count": target_word_count,
        "draft": draft,
    })

    try:
        result = llm_with_structure.invoke(eval_prompt)

        logger.info(f"    ✓ Coverage score: {result.coverage_score:.2f}")
        logger.info(f"    ✓ Satisfied: {'Yes' if result.is_satisfied else 'No'}")

        if not result.is_satisfied and result.follow_up_queries:
            logger.info(f"    ↳ Follow-up queries: {len(result.follow_up_queries)}")
            for i, q in enumerate(result.follow_up_queries, 1):
                logger.info(f"      {i}. {q}")

        return {
            "is_satisfied": result.is_satisfied,
            "follow_up_queries": result.follow_up_queries if not result.is_satisfied else []
        }

    except Exception as e:
        logger.error(f"    ⚠️  Evaluation failed: {e}")
        draft_length = len(draft)
        is_satisfied = draft_length >= target_word_count * 0.8
        logger.info(f"    ↳ Fallback evaluation: draft length {draft_length} characters")

        return {
            "is_satisfied": is_satisfied,
            "follow_up_queries": []
        }


# ============================================================
# Conditional Edge Function (returns Send list or "finalize")
# ============================================================

def route_after_evaluate(state: ChapterIterativeState):
    """
    Conditional edge: determine whether to continue or finalize

    Rules:
    1. If iteration >= MAX_ITERATIONS → "finalize" (强制终止)
    2. If is_satisfied=True OR follow_up_queries is empty → "finalize"
    3. If is_satisfied=False AND follow_up_queries has items → Send to search

    Returns: "finalize" or List[Send]
    """
    chapter_id = state["chapter_id"]
    chapter_outline = state["chapter_outline"]
    iteration = state.get("iteration", 0)
    is_satisfied = state.get("is_satisfied", False)
    follow_up_queries = state.get("follow_up_queries", [])

    logger.info(f"  🔀 [Chapter {chapter_id}] Decision point...")
    logger.info(f"    ↳ Iteration: {iteration}/{MAX_ITERATIONS}")
    logger.info(f"    ↳ Satisfied: {is_satisfied}")
    logger.info(f"    ↳ Follow-up queries: {len(follow_up_queries)}")

    # 检查是否达到最大迭代次数
    if iteration >= MAX_ITERATIONS:
        logger.warning(f"    ⚠️  Max iterations ({MAX_ITERATIONS}) reached, forcing finalize")
        return "finalize"

    # Finalize if satisfied or no follow-up queries
    if is_satisfied or not follow_up_queries:
        logger.success(f"    ✓ Finalizing chapter")
        return "finalize"

    # Send follow-up queries to search
    logger.info(f"    ↳ Dispatching {len(follow_up_queries)} follow-up searches...")
    return [
        Send("search", {
            "chapter_id": chapter_id,
            "chapter_outline": chapter_outline,
            "search_query": query,
        })
        for query in follow_up_queries
    ]


# ============================================================
# Final Node
# ============================================================

def finalize_node(state: ChapterIterativeState) -> Dict[str, Any]:
    """
    Final node: prepare output
    """
    chapter_id = state["chapter_id"]
    draft = state.get("draft", "")
    iteration = state.get("iteration", 0)

    logger.success(f"  🎉 [Chapter {chapter_id}] Content generation completed (Total iterations: {iteration})")

    return {
        "final_content": draft
    }
