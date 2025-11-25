"""
Chapter Content Generation Agent - 迭代式章节内容生成的图构建
"""
from loguru import logger
from langgraph.graph import StateGraph, END

from app.agents.core.publisher.subgraphs.chapter_content_generation.state import ChapterIterativeState
from app.agents.core.publisher.subgraphs.chapter_content_generation.nodes import (
    generate_queries_node,
    search_node,
    write_node,
    evaluate_node,
    should_continue_iteration,
    finalize_node
)


def create_iterative_chapter_subgraph():
    """
    创建迭代式章节内容生成 Subgraph

    流程:
        START
          ↓
        generate_queries (生成 queries，Send 并行搜索)
          ↓
        search (并行执行，结果通过 reducer 汇总)
          ↓
        write (基于搜索结果写/完善草稿，清空 search_results)
          ↓
        evaluate (评估，返回 missing_content)
          ↓
        should_continue (条件边)
            ├─ "continue" → 回到 generate_queries (根据 missing_content 生成补充 queries)
            └─ "finalize" → finalize → END
    """
    logger.info("🏗️  构建迭代式章节内容生成 Subgraph")

    # 创建 StateGraph
    subgraph = StateGraph(ChapterIterativeState)

    # 添加节点
    subgraph.add_node("generate_queries", generate_queries_node)
    subgraph.add_node("search", search_node)
    subgraph.add_node("write", write_node)
    subgraph.add_node("evaluate", evaluate_node)
    subgraph.add_node("finalize", finalize_node)

    # 设置入口点
    subgraph.set_entry_point("generate_queries")

    # generate_queries 使用 Command(goto=sends)，LangGraph 会自动处理并行
    # search 执行完后进入 write
    subgraph.add_edge("search", "write")
    subgraph.add_edge("write", "evaluate")

    # 添加条件边：根据评估结果决定是继续还是结束
    subgraph.add_conditional_edges(
        "evaluate",
        should_continue_iteration,
        {
            "continue": "generate_queries",  # 不满意：回到 generate_queries 生成补充 queries
            "finalize": "finalize"           # 满意或达到最大迭代次数：结束
        }
    )

    # 最终边
    subgraph.add_edge("finalize", END)

    logger.success("✅ 迭代式章节内容生成 Subgraph 构建完成")

    # 编译并返回
    return subgraph.compile()
