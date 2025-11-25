"""
Chapter Content Generation State - 迭代式章节内容生成的状态定义
"""
import operator
from typing import TypedDict, List, Any, Annotated


class SearchResult(TypedDict):
    """单个搜索结果"""
    query: str
    content: str


class ChapterIterativeState(TypedDict):
    """
    迭代式章节生成的状态（精简版）

    chapter_outline 包含所有章节信息:
    - title, description, content_requirements, writing_guidance, estimated_words
    """
    # ========== 输入 ==========
    chapter_id: int
    chapter_outline: Any  # Section 对象

    # ========== 中间状态 ==========
    search_results: Annotated[List[SearchResult], operator.add]  # 并行搜索汇总，write 后清空
    draft: str
    iteration: int

    # ========== evaluate 输出 ==========
    is_satisfied: bool
    follow_up_queries: List[str]  # evaluate 生成的后续查询，为空表示满意

    # ========== 最终输出 ==========
    final_content: str
