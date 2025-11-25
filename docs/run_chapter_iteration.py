"""
Test for Chapter Content Generation Subgraph

直接运行整个 graph，测试完整迭代流程

流程:
1. generate_queries: 生成 3 个 queries，并行 Send
2. search: 并行执行搜索，结果汇总
3. write: 基于搜索结果写草稿，清空 search_results
4. evaluate: 评估 → 返回 missing_content
5. 如果不满意 → 回到 generate_queries 根据 missing_content 生成补充 queries

运行方式: python docs/run_chapter_iteration.py
"""
from pydantic import BaseModel

from app.agents.core.publisher.subgraphs.chapter_content_generation import (
    create_iterative_chapter_subgraph
)


# ============================================================
# Mock Data
# ============================================================

class MockSection(BaseModel):
    """Mock Section object to simulate chapter_outline"""
    title: str
    description: str
    writing_guidance: str
    content_requirements: str = ""
    visual_elements: str = ""
    estimated_words: int = 1200
    writing_priority: str = "high"


test_blueprint = {
    "title": "四、AI硬件基础设施",
    "description": "深入分析AI发展的硬件支撑体系，重点探讨GPU、TPU等AI专用芯片的技术演进、性能特点和发展趋势。涵盖计算架构创新、能效优化、专用硬件生态等关键维度，展现硬件基础设施对AI技术发展的基础性支撑作用。",
    "writing_guidance": "采用技术演进+性能对比+应用需求的分析框架。先梳理硬件发展历程，再对比主要芯片技术特点，最后分析硬件需求与AI应用发展的互动关系。突出硬件瓶颈突破对AI技术进步的推动作用。",
    "content_requirements": "GPU、TPU等主流芯片的技术参数对比数据，代表性硬件厂商案例，硬件性能演进趋势图表",
    "visual_elements": "芯片架构对比图、性能演进曲线、硬件生态图谱",
    "estimated_words": 1200,
    "writing_priority": "high"
}


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Testing Chapter Content Generation Subgraph (Refactored)")
    print("=" * 70)
    print("Flow: generate_queries -> search (parallel) -> write -> evaluate")
    print("      -> (if not satisfied) -> generate_queries (with missing_content) -> ...")

    # 创建 mock section
    mock_section = MockSection(**test_blueprint)

    # 创建初始 state (精简版)
    initial_state = {
        "chapter_id": 4,
        "chapter_outline": mock_section,
        # 以下字段会在运行过程中填充
        "missing_content": "",
        "search_results": [],
        "draft": "",
        "iteration": 0,
        "is_satisfied": False,
        "final_content": "",
    }

    print(f"\nChapter: {mock_section.title}")
    print(f"Target words: {mock_section.estimated_words}")
    print(f"Priority: {mock_section.writing_priority}")
    print("\n" + "-" * 70)

    # 创建并运行 graph
    graph = create_iterative_chapter_subgraph()
    final_state = graph.invoke(initial_state)

    # 打印结果
    print("\n" + "=" * 70)
    print("GRAPH EXECUTION COMPLETED")
    print("=" * 70)

    print(f"\nFinal Results:")
    print(f"  - Total iterations: {final_state.get('iteration', 'N/A')}")
    print(f"  - Is satisfied: {final_state.get('is_satisfied', 'N/A')}")
    print(f"  - Final content length: {len(final_state.get('final_content', ''))} characters")

    if final_state.get('missing_content'):
        print(f"\nLast missing_content (if any):")
        print(f"  {final_state['missing_content'][:200]}...")

    print("\n" + "-" * 70)
    print("Final Content Preview (first 1500 chars):")
    print("-" * 70)
    print(final_state.get('final_content', '')[:1500])
    print("\n" + "=" * 70)
