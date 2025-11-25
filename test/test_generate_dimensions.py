import json
from pydantic import BaseModel
from typing import List

from app.agents.core.publisher.subgraphs.chapter_content_generation.nodes import generate_dimensions_node


# ============================================================
# Test Blueprint (Fill this with your actual blueprint section)
# ============================================================

test_blueprint = """
{
  "title": "三、AI技术基础",
  "description": "深入解析AI的核心技术体系和关键突破，为理解AI应用和发展趋势提供技术支撑。涵盖机器学习、自然语言处理、计算机视觉等基础技术领域，以及大语言模型、生成式AI、多模态系统等前沿突破。",
  "writing_guidance": "技术讲解与实例分析相结合，既要保证技术准确性又要确保可读性。采用分类讲解方式，突出各技术的特点和应用价值。适当使用技术对比和性能指标说明。",
  "content_requirements": "核心技术原理资料、技术性能对比数据、代表性模型参数",
  "visual_elements": "技术架构图、性能对比表格、模型演进路线图",
  "estimated_words": 1200,
  "writing_priority": "high"
}
"""


# ============================================================
# Mock Section Class
# ============================================================

class MockSection(BaseModel):
    """Mock Section object to simulate chapter_outline"""
    title: str
    description: str
    writing_guidance: str
    content_requirements: str = ""
    visual_elements: str = ""
    estimated_words: int = 800
    writing_priority: str = "medium"


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":
    # Parse blueprint
    blueprint_data = json.loads(test_blueprint)
    mock_section = MockSection(**blueprint_data)

    # Create test state
    test_state = {
        "chapter_id": 3,
        "chapter_outline": mock_section,
        "document_outline": None,
        "target_word_count": mock_section.estimated_words,
    }

    # Call the node
    print("=" * 60)
    print("🧪 Testing generate_dimensions_node")
    print("=" * 60)
    print(f"\nChapter: {mock_section.title}")
    print(f"Priority: {mock_section.writing_priority}")
    print(f"Target words: {mock_section.estimated_words}")
    print("\n" + "-" * 60)

    result = generate_dimensions_node(test_state)

    # Print results
    print("\n📊 Results:")
    print(f"Generated {len(result['dimensions'])} dimensions:\n")

    for i, dim in enumerate(result['dimensions'], 1):
        print(f"{i}. {dim['dimension_name']}")
        print(f"   Coverage: {dim['coverage_requirement']}")
        print(f"   Keywords: {dim['keywords']}\n")

    print("-" * 60)
    print(f"✅ Iteration: {result['iteration']}")
    print(f"✅ Draft: '{result['draft']}'")
    print(f"✅ Is satisfied: {result['is_satisfied']}")
    print("=" * 60)
