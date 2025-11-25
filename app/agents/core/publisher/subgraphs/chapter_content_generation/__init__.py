"""
Chapter Content Generation Subgraph - 迭代式章节内容生成

流程:
1. generate_queries: 根据 chapter 或 missing_content 生成 queries，并行 Send
2. search: 并行执行搜索，结果通过 reducer 汇总
3. write: 基于搜索结果撰写/完善草稿，清空 search_results
4. evaluate: 评估草稿，返回 missing_content
5. 根据评估结果决定是否继续（回到 generate_queries）

最大迭代次数: 3 轮
"""

from app.agents.core.publisher.subgraphs.chapter_content_generation.agent import (
    create_iterative_chapter_subgraph
)
from app.agents.core.publisher.subgraphs.chapter_content_generation.state import (
    ChapterIterativeState,
    SearchResult
)

__all__ = [
    "create_iterative_chapter_subgraph",
    "ChapterIterativeState",
    "SearchResult"
]
