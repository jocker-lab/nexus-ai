"""
Chapter Content Generation State - 迭代式章节内容生成的状态定义
"""
from typing import TypedDict, List, Any, Annotated, Optional, Union

from app.agents.schemas.document_outline_schema import DocumentOutline


class SearchResult(TypedDict):
    """单个搜索结果"""
    query: str
    content: str


def search_results_reducer(
    current: List[SearchResult],
    update: Union[List[SearchResult], None]
) -> List[SearchResult]:
    """
    自定义 reducer 处理 search_results 的并发更新和清空

    - update 是 None → 清空列表（用于 write_node 后清空）
    - update 是列表 → 追加到当前列表（用于并行搜索汇总）
    """
    if update is None:
        return []
    return current + update


class ChapterIterativeState(TypedDict):
    """
    迭代式章节生成的状态

    支持两阶段流程:
    1. 素材搜索 + 写作迭代循环
    2. 与 section_writer 的 reviewer/reviser 循环集成
    """
    # ========== 输入（从 section_writer 或父图传入）==========
    chapter_id: int
    chapter_outline: Any  # Section 对象


    # 写作上下文（用于生成符合风格的内容）
    document_outline: Optional[DocumentOutline]  # 整体文档大纲
    writer_role: Optional[str]  # 作者角色
    writer_profile: Optional[str]  # 作者简介
    writing_principles: Optional[List[str]]  # 写作原则

    # ========== 中间状态 ==========
    # 使用自定义 reducer：支持并行搜索汇总 + write 后清空
    search_results: Annotated[List[SearchResult], search_results_reducer]
    draft: str  # 当前草稿（也是最终输出给 reviewer 的内容）
    iteration: int  # 素材搜索迭代次数

    # ========== evaluate 输出 ==========
    is_satisfied: bool
    follow_up_queries: List[str]  # evaluate 生成的后续查询，为空表示满意

    # ========== 最终输出 ==========
    final_content: str  # finalize 后的最终内容（与 draft 相同）
