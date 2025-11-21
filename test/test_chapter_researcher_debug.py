# -*- coding: utf-8 -*-
"""
@File    :   test_chapter_researcher_debug.py
@Time    :   2025/11/20
@Author  :   Claude
@Version :   2.0
@Desc    :   Chapter Researcher 调试版本 - 带详细日志追踪搜索和summarization
"""

import asyncio
from loguru import logger
from dotenv import load_dotenv
import sys

# 🔥 加载环境变量
load_dotenv()

from app.agents.core.publisher.subgraphs.chapter_writing.nodes.chapter_researcher import chapter_researcher
from app.agents.schemas.document_outline_schema import Section, SubSection, DocumentOutline


# ==================== 测试数据 ====================

def create_test_chapter_outline():
    """创建测试章节大纲"""
    return Section(
        title="AI技术市场现状与趋势",
        description=(
            "本章节全面分析人工智能技术在2024-2025年的市场发展现状，"
            "包括市场规模、主要参与者、技术应用场景和未来发展趋势。"
        ),
        writing_guidance=(
            "采用数据驱动的分析方法，优先引用权威市场研究机构的数据。"
        ),
        content_requirements=(
            "需要以下数据：(1) 2024年全球AI市场规模（Gartner/IDC）, "
            "(2) 中国AI市场份额和增长率, "
            "(3) 生成式AI应用案例（至少3-5个）, "
            "(4) 2025年AI技术发展趋势预测。"
        ),
        visual_elements=True,
        estimated_words=1200,
        writing_priority="high",
        subsections=[
            SubSection(
                sub_section_title="全球AI市场规模分析",
                description="分析2024年全球人工智能市场的总体规模、区域分布和增长速度。",
                writing_guidance="以具体数字开篇，引用至少2个权威机构的数据。",
                estimated_word_count=400
            ),
            SubSection(
                sub_section_title="生成式AI技术应用热点",
                description="聚焦生成式AI在各行业的具体应用场景。",
                writing_guidance="采用案例分析法，每个领域提供1-2个典型应用实例。",
                estimated_word_count=500
            ),
        ]
    )


def create_test_document_outline():
    """创建文档大纲"""
    return DocumentOutline(
        title="2025年企业AI应用战略报告",
        language="zh-CN",
        target_audience="企业CTO、技术决策者",
        writing_style="business",
        writing_tone="authoritative",
        writing_purpose="为企业技术决策者提供AI技术应用的全景分析",
        key_themes=["AI技术市场分析", "企业应用场景"],
        estimated_total_words=8000,
        sections=[create_test_chapter_outline()]
    )


# ==================== 猴子补丁：追踪所有搜索调用 ====================

def patch_searcher_with_logging():
    """
    给 searcher 函数添加日志追踪
    """
    from app.agents.tools.search import tavily_search
    import functools

    search_call_count = [0]  # 使用列表来在闭包中修改

    # 保存原始函数
    original_func = tavily_search.searcher.func

    @functools.wraps(original_func)
    def logged_searcher(query: str):
        search_call_count[0] += 1
        call_num = search_call_count[0]

        logger.info("")
        logger.info("=" * 100)
        logger.info(f"🔍 SEARCH CALL #{call_num}")
        logger.info("=" * 100)
        logger.info(f"📝 Query: {query}")

        # 调用原始函数
        result = original_func(query)

        # 分析返回结果
        if isinstance(result, str):
            logger.info(f"📄 Result length: {len(result)} characters")
            logger.info(f"   Preview: {result[:300]}...")
        else:
            logger.info(f"📊 Result type: {type(result)}")

        logger.info("=" * 100)
        logger.info("")

        return result

    # 替换原函数
    tavily_search.searcher.func = logged_searcher
    logger.success("✅ Searcher logging patch applied")


def patch_deepagent_with_logging():
    """
    给 create_deep_agent 添加日志追踪
    """
    from deepagents import graph

    original_create_deep_agent = graph.create_deep_agent

    agent_count = [0]

    def logged_create_deep_agent(*args, **kwargs):
        agent_count[0] += 1
        agent_id = agent_count[0]

        logger.info("")
        logger.info("🤖" * 50)
        logger.info(f"🤖 DEEP AGENT #{agent_id} CREATED")
        logger.info("🤖" * 50)
        logger.info(f"   Model: {kwargs.get('model', args[0] if args else 'default')}")
        logger.info(f"   Tools: {len(kwargs.get('tools', []))} tools")
        logger.info(f"   System Prompt Length: {len(kwargs.get('system_prompt', '')) if kwargs.get('system_prompt') else 0} chars")
        logger.info("🤖" * 50)
        logger.info("")

        return original_create_deep_agent(*args, **kwargs)

    graph.create_deep_agent = logged_create_deep_agent
    logger.success("✅ DeepAgent logging patch applied")


# ==================== 主测试函数 ====================

async def test_with_detailed_logging():
    """
    带详细日志的测试
    """
    logger.info("\n" + "🎯" * 50)
    logger.info("🎯 开始调试测试：追踪搜索和Summarization")
    logger.info("🎯" * 50 + "\n")

    # 应用补丁
    logger.info("📦 应用日志追踪补丁...")
    patch_searcher_with_logging()
    patch_deepagent_with_logging()
    logger.info("")

    # 构建测试状态
    test_state = {
        "chapter_id": 1,
        "document_outline": create_test_document_outline(),
        "chapter_outline": create_test_chapter_outline(),
        "target_word_count": 1200,
    }

    logger.info("📋 测试配置:")
    logger.info(f"   Chapter Title: {test_state['chapter_outline'].title}")
    logger.info(f"   Target Words: {test_state['target_word_count']}")
    logger.info(f"   Subsections: {len(test_state['chapter_outline'].subsections)}")
    logger.info("")

    logger.info("🚀 开始执行 chapter_researcher...")
    logger.info("=" * 100)
    logger.info("")

    # 执行研究
    try:
        result = await chapter_researcher(test_state)

        logger.info("")
        logger.info("=" * 100)
        logger.info("✅ RESEARCH COMPLETED")
        logger.info("=" * 100)

        # 分析结果
        materials = result.get("synthesized_materials", "")
        logger.info(f"📊 研究素材长度: {len(materials):,} 字符")
        logger.info(f"📄 研究素材预览（前500字符）:")
        logger.info("-" * 100)
        logger.info(materials[:500])
        logger.info("-" * 100)

        # 统计Topic数量
        topic_count = materials.count("Topic:")
        logger.info(f"📌 研究主题数量: {topic_count}")

        # 检查是否有summarization的痕迹
        if "summary" in materials.lower() or "总结" in materials:
            logger.warning("⚠️  结果中可能包含 summarization 内容！")

        return result

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    """
    运行方式：
        python test/test_chapter_researcher_debug.py
    """

    # 配置 loguru 输出格式
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

    # 运行测试
    asyncio.run(test_with_detailed_logging())
