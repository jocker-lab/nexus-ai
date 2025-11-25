import json
from pydantic import BaseModel
from typing import List

from app.agents.core.publisher.subgraphs.chapter_content_generation.nodes import generate_dimensions_node


# ============================================================
# Test Blueprint (Fill this with your actual blueprint section)
# ============================================================

test_blueprint = """
{
      "title": "四、AI芯片与硬件基础设施",
      "description": "深入分析AI发展的硬件支撑体系，重点探讨GPU、TPU等AI专用芯片的技术演进、性能特点和发展趋势。涵盖计算架构创新、能效优化、专用硬件生态等关键维度，展现硬件基础设施对AI技术发展的基础性支撑作用。",
      "writing_guidance": "采用技术演进+性能对比+应用需求的分析框架。先梳理硬件发展历程，再对比主要芯片技术特点，最后分析硬件需求与AI应用发展的互动关系。突出硬件瓶颈突破对AI技术进步的推动作用。",
      "content_requirements": "AI芯片技术参数、性能基准测试数据、硬件发展路线图、能效对比分析",
      "visual_elements": "AI芯片性能对比图、硬件架构演进图、能效对比表格",
      "estimated_words": 1000,
      "writing_priority": "high",
      "subsections": [
        {
          "sub_section_title": "AI专用芯片发展",
          "description": "系统分析GPU、TPU、NPU等AI专用芯片的技术演进路径和性能特点。探讨从通用计算到专用计算的转变趋势，分析不同架构芯片在训练、推理等AI任务中的适用性和效率优势。",
          "writing_guidance": "按芯片类型分类分析，每个类型从架构特点、性能指标、应用场景三个维度展开。使用具体技术参数和基准测试数据支撑分析结论。",
          "estimated_word_count": 500
        },
        {
          "sub_section_title": "硬件基础设施生态",
          "description": "全面分析AI硬件基础设施的生态系统，包括数据中心建设、边缘计算设备、专用服务器集群等。探讨硬件基础设施的规模化部署、能效优化和成本控制等关键问题，以及不同应用场景的硬件需求差异。",
          "writing_guidance": "从基础设施层级展开分析，涵盖数据中心、边缘设备、终端芯片等不同层面。采用需求-供给-挑战的分析框架，突出硬件基础设施对AI应用落地的支撑作用。",
          "estimated_word_count": 500
        }
      ]
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
