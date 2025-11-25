"""
Chapter Content Generation Nodes - Iterative Chapter Generation Implementation
"""
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
    missing_content: str = Field(description="Description of what content is missing or needs improvement. Empty string if satisfied.")


# ============================================================
# Node 1: Generate Queries and Dispatch Parallel Search
# ============================================================

def generate_queries_node(state: ChapterIterativeState) -> Command:
    """
    Node 1: Generate search queries and dispatch parallel searches

    - 第一轮 (missing_content 为空): 根据 chapter 信息生成 3 个 queries
    - 后续轮 (missing_content 有值): 根据缺失内容生成 1-3 个补充 queries

    Output: Command with Send list to search_node
    """
    chapter_id = state["chapter_id"]
    chapter_outline = state["chapter_outline"]
    chapter_title = chapter_outline.title
    chapter_description = getattr(chapter_outline, "description", "")
    content_requirements = getattr(chapter_outline, "content_requirements", "")
    writing_guidance = getattr(chapter_outline, "writing_guidance", "")

    missing_content = state.get("missing_content", "")
    iteration = state.get("iteration", 0)
    draft = state.get("draft", "")

    llm = ChatDeepSeek(model="deepseek-chat", temperature=0)
    llm_with_structure = llm.with_structured_output(QueryList)

    # 根据 missing_content 选择不同的模板
    if not missing_content:
        logger.info(f"  🔍 [Chapter {chapter_id}] Generating initial search queries...")
        prompt = render_prompt_template(f"{PROMPT_PATH}/generate_queries_initial", {
            "chapter_title": chapter_title,
            "chapter_description": chapter_description,
            "content_requirements": content_requirements,
            "writing_guidance": writing_guidance,
        })
    else:
        logger.info(f"  🔍 [Chapter {chapter_id}] Generating supplementary queries (iteration {iteration + 1})...")
        prompt = render_prompt_template(f"{PROMPT_PATH}/generate_queries_supplement", {
            "chapter_title": chapter_title,
            "chapter_description": chapter_description,
            "missing_content": missing_content,
        })

    try:
        result = llm_with_structure.invoke(prompt)
        queries = result.queries[:3]  # Ensure max 3 queries

        logger.info(f"    ✓ Generated {len(queries)} queries:")
        for i, query in enumerate(queries, 1):
            logger.info(f"      {i}. {query}")

        # Build Send list for parallel search
        send_list = []
        for query in queries:
            send_list.append(Send("search", {
                "chapter_id": chapter_id,
                "chapter_outline": chapter_outline,
                "current_query": query,
                "missing_content": missing_content,
                "search_results": [],
                "draft": draft,
                "iteration": iteration,
                "is_satisfied": False,
                "final_content": "",
            }))

        logger.info(f"    ✓ Dispatching {len(send_list)} parallel searches...")

        return Command(goto=send_list)

    except Exception as e:
        logger.error(f"    ⚠️  Query generation failed: {e}")
        fallback_query = f"{chapter_title} {content_requirements}" if not missing_content else f"{chapter_title} {missing_content}"
        logger.info(f"    ↳ Using fallback query: {fallback_query}")

        return Command(goto=[Send("search", {
            "chapter_id": chapter_id,
            "chapter_outline": chapter_outline,
            "current_query": fallback_query,
            "missing_content": missing_content,
            "search_results": [],
            "draft": draft,
            "iteration": iteration,
            "is_satisfied": False,
            "final_content": "",
        })])


# ============================================================
# Node 2: Search (Pure Search Node)
# ============================================================

def search_node(state: ChapterIterativeState) -> Dict[str, Any]:
    """
    Node 2: Pure search execution (supports parallel execution)

    Input: current_query (passed via Send)
    Output: search_results (list with single result, aggregated by operator.add)
    """
    chapter_id = state["chapter_id"]
    current_query = state.get("current_query", "")

    logger.info(f"  🔍 [Chapter {chapter_id}] Searching...")
    logger.info(f"    Query: {current_query}")

    try:
        from app.agents.tools.search.tavily_search import searcher
    except ImportError:
        logger.error("    ⚠️  Cannot import search tool")
        return {
            "search_results": [{
                "query": current_query,
                "content": f"Search tool unavailable. Placeholder content for: {current_query}"
            }]
        }

    try:
        search_content = searcher.invoke(current_query, max_results=5)
        logger.info(f"    ✓ Search completed ({len(search_content)} characters)")

        return {
            "search_results": [{
                "query": current_query,
                "content": search_content
            }]
        }

    except Exception as e:
        logger.error(f"    ⚠️  Search failed: {e}")
        return {
            "search_results": [{
                "query": current_query,
                "content": f"Search failed: {str(e)}. Query was: {current_query}"
            }]
        }


# ============================================================
# Node 3: Write/Refine Draft (Agent with Chart Generation)
# ============================================================

async def write_node(state: ChapterIterativeState) -> Dict[str, Any]:
    """
    Node 3: Write or refine draft using Agent with chart generation capability

    Input: search_results (list), draft, iteration, chapter_outline
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

    logger.info(f"  ✍️  [Chapter {chapter_id}] Writing draft (iteration {iteration + 1})...")
    if visual_elements:
        logger.info(f"    ↳ Chart generation enabled")

    # Initialize LLM
    llm = init_chat_model("deepseek:deepseek-chat")

    # Format search results
    search_results_text = "\n\n---\n\n".join([
        f"**Query**: {r['query']}\n**Results**:\n{r['content']}"
        for r in search_results_list
    ]) if search_results_list else "No search results available."

    # Load system prompt
    system_prompt = render_prompt_template(f"{PROMPT_PATH}/write_draft_system", {
        "visual_elements": visual_elements,
    })

    # Create Agent with tools
    agent = create_agent(
        model=llm,
        tools=[generate_chart, think, criticize],
        system_prompt=system_prompt
    )

    # Choose task prompt based on iteration
    if iteration == 0:
        user_prompt = render_prompt_template(f"{PROMPT_PATH}/write_draft_initial", {
            "chapter_title": chapter_title,
            "description": description,
            "content_requirements": content_requirements,
            "writing_guidance": writing_guidance,
            "search_results_text": search_results_text,
            "target_word_count": target_word_count,
            "visual_elements": visual_elements,
        })
    else:
        user_prompt = render_prompt_template(f"{PROMPT_PATH}/write_draft_refine", {
            "chapter_title": chapter_title,
            "description": description,
            "content_requirements": content_requirements,
            "draft": draft,
            "search_results_text": search_results_text,
            "target_word_count": target_word_count,
            "visual_elements": visual_elements,
        })

    try:
        logger.info(f"    ↳ Starting Agent (with chart generation capability)...")

        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_prompt}]},
            config={"recursion_limit": 50}
        )

        # Extract final content (last AI message)
        ai_messages = [m for m in response["messages"] if isinstance(m, AIMessage) and m.content]

        if ai_messages:
            new_draft = ai_messages[-1].content.strip()
        else:
            raise ValueError("Agent did not return valid content")

        logger.info(f"    ✓ Draft length: {len(new_draft)} characters")
        logger.info(f"    ✓ Charts generated: {new_draft.count('![')}")

        return {
            "draft": new_draft,
            "iteration": iteration + 1,
            "search_results": []  # 清空 search_results，为下一轮准备
        }

    except Exception as e:
        logger.error(f"    ⚠️  Writing failed: {e}")
        import traceback
        traceback.print_exc()
        fallback_draft = draft if draft else f"# {chapter_title}\n\nWriting failed: {str(e)}"
        return {
            "draft": fallback_draft,
            "iteration": iteration + 1,
            "search_results": []
        }


# ============================================================
# Node 4: Evaluate Draft Quality
# ============================================================

def evaluate_node(state: ChapterIterativeState) -> Dict[str, Any]:
    """
    Node 4: Evaluate draft quality

    Input: draft, chapter_outline
    Output: is_satisfied, missing_content (str describing what's missing)
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

        if not result.is_satisfied and result.missing_content:
            logger.info(f"    ↳ Missing: {result.missing_content[:100]}...")

        return {
            "is_satisfied": result.is_satisfied,
            "missing_content": result.missing_content if not result.is_satisfied else ""
        }

    except Exception as e:
        logger.error(f"    ⚠️  Evaluation failed: {e}")
        draft_length = len(draft)
        is_satisfied = draft_length >= target_word_count * 0.8
        logger.info(f"    ↳ Fallback evaluation: draft length {draft_length} characters")

        return {
            "is_satisfied": is_satisfied,
            "missing_content": "" if is_satisfied else "Unable to evaluate properly, needs general improvement"
        }


# ============================================================
# Conditional Edge Function
# ============================================================

def should_continue_iteration(state: ChapterIterativeState) -> str:
    """
    Conditional edge: determine whether to continue iterating

    Rules:
    1. If satisfied → "finalize"
    2. If not satisfied but iteration < max_iterations → "continue"
    3. If iteration >= max_iterations → "finalize" (force stop)
    """
    chapter_id = state["chapter_id"]
    iteration = state.get("iteration", 0)
    is_satisfied = state.get("is_satisfied", False)

    max_iterations = 3

    logger.info(f"  🔀 [Chapter {chapter_id}] Decision point...")
    logger.info(f"    ↳ Iteration: {iteration}/{max_iterations}")
    logger.info(f"    ↳ Satisfied: {is_satisfied}")

    if iteration >= max_iterations:
        logger.info(f"    ✓ Max iterations reached, forcing finalization")
        return "finalize"

    if is_satisfied:
        logger.success(f"    ✓ Draft satisfactory, early termination")
        return "finalize"

    logger.info(f"    ↳ Continuing to next iteration (back to generate_queries)")
    return "continue"


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
