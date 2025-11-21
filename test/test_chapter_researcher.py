# -*- coding: utf-8 -*-
"""
@File    :   test_chapter_researcher.py
@Time    :   2025/11/18
@Author  :   Claude
@Version :   1.0
@Desc    :   Chapter Researcher 节点单元测试
"""

import asyncio
import pytest
from loguru import logger
from dotenv import load_dotenv

# 🔥 加载环境变量（从项目根目录的 .env 文件）
load_dotenv()

from app.agents.core.publisher.subgraphs.chapter_writing.nodes.chapter_researcher import chapter_researcher
from app.agents.schemas.document_outline_schema import Section, SubSection, DocumentOutline


# ==================== 测试数据：模拟章节大纲 ====================

def create_test_chapter_outline_1():
    """
    测试用例1：AI技术市场分析章节
    包含多个子章节，需要广泛的市场数据研究
    """
    return Section(
        title="AI技术市场现状与趋势",
        description=(
            "本章节全面分析人工智能技术在2024-2025年的市场发展现状，"
            "包括市场规模、主要参与者、技术应用场景和未来发展趋势。"
            "重点关注生成式AI和大语言模型领域的最新进展。"
        ),
        writing_guidance=(
            "采用数据驱动的分析方法，优先引用权威市场研究机构的数据。"
            "结构上采用'现状→趋势→预测'的逻辑顺序。"
            "重点突出中国市场与全球市场的对比分析。"
            "建议使用图表可视化市场规模增长趋势。"
        ),
        content_requirements=(
            "需要以下数据：(1) 2024年全球AI市场规模（Gartner/IDC）, "
            "(2) 中国AI市场份额和增长率, "
            "(3) 主要AI公司财报数据（OpenAI/谷歌/百度/阿里）, "
            "(4) 生成式AI应用案例（至少3-5个）, "
            "(5) 行业专家对2025年趋势的预测。"
        ),
        visual_elements=True,
        estimated_words=1200,  # ✅ 正确的字段名
        writing_priority="high",
        subsections=[
            SubSection(
                sub_section_title="全球AI市场规模分析",
                description=(
                    "分析2024年全球人工智能市场的总体规模、区域分布和增长速度。"
                    "对比不同研究机构的数据，提供可靠的市场规模估算。"
                ),
                writing_guidance=(
                    "以具体数字开篇，引用至少2个权威机构的数据。"
                    "使用柱状图展示不同区域的市场份额。"
                    "分析驱动市场增长的关键因素。"
                ),
                estimated_word_count=400  # ✅ SubSection 的字段名正确
            ),
            SubSection(
                sub_section_title="生成式AI技术应用热点",
                description=(
                    "聚焦生成式AI在各行业的具体应用场景，"
                    "包括内容创作、代码生成、客户服务、医疗诊断等领域。"
                ),
                writing_guidance=(
                    "采用案例分析法，每个领域提供1-2个典型应用实例。"
                    "强调技术落地的商业价值和ROI数据。"
                ),
                estimated_word_count=500
            ),
            SubSection(
                sub_section_title="2025年AI技术发展趋势",
                description=(
                    "基于当前技术发展和专家预测，分析2025年AI领域的关键趋势，"
                    "包括多模态模型、AI Agent、行业垂直化等方向。"
                ),
                writing_guidance=(
                    "结合技术论文和行业报告，突出新兴趋势。"
                    "引用行业领袖的前瞻性观点。"
                ),
                estimated_word_count=300
            ),
        ]
    )


def create_test_chapter_outline_2():
    """
    测试用例2：企业数字化转型挑战
    侧重于案例研究和问题分析
    """
    return Section(
        title="企业数字化转型面临的主要挑战",
        description=(
            "深入分析传统企业在数字化转型过程中遇到的核心障碍，"
            "包括组织结构、技术债务、人才短缺和文化变革等方面。"
            "通过典型案例揭示成功与失败的关键差异。"
        ),
        writing_guidance=(
            "采用问题导向的分析框架，先现象后原因。"
            "每个挑战领域提供至少1个真实企业案例。"
            "强调可操作的应对策略，避免空泛的理论讨论。"
        ),
        content_requirements=(
            "需要：(1) 数字化转型失败率统计数据, "
            "(2) 3-5个企业转型案例（成功和失败各有）, "
            "(3) IT预算分配数据, "
            "(4) 技术人才缺口报告, "
            "(5) 麦肯锡/德勤等咨询公司的转型研究报告。"
        ),
        visual_elements=False,
        estimated_words=1000,  # ✅ 正确的字段名
        writing_priority="medium",
        subsections=[
            SubSection(
                sub_section_title="组织架构与文化阻力",
                description=(
                    "分析传统层级制组织如何阻碍敏捷转型，"
                    "以及员工对新技术的抵触心理及其根源。"
                ),
                writing_guidance=(
                    "以具体企业的组织变革案例为切入点。"
                    "对比传统架构与数字化组织的结构差异。"
                ),
                estimated_word_count=350  # ✅ SubSection 的字段名正确
            ),
            SubSection(
                sub_section_title="技术债务与遗留系统",
                description=(
                    "探讨如何处理旧系统的兼容性问题，"
                    "以及技术栈迁移的成本与风险。"
                ),
                writing_guidance=(
                    "引用实际的系统迁移成本数据。"
                    "提供渐进式重构的实践建议。"
                ),
                estimated_word_count=350
            ),
            SubSection(
                sub_section_title="数字化人才缺口",
                description=(
                    "分析企业在招聘和培养数字化人才方面的困难，"
                    "包括技能需求变化和人才市场竞争。"
                ),
                writing_guidance=(
                    "使用人才市场供需数据支撑论点。"
                    "提及培训和外包作为补充策略。"
                ),
                estimated_word_count=300
            ),
        ]
    )


def create_test_document_outline():
    """
    创建完整的文档大纲（用于提供全局上下文）
    """
    return DocumentOutline(
        title="2025年企业AI应用战略报告",
        language="zh-CN",
        target_audience="企业CTO、技术决策者、战略规划人员",
        writing_style="business",
        writing_tone="authoritative",
        writing_purpose=(
            "为企业技术决策者提供AI技术应用的全景分析和可执行的战略建议，"
            "帮助企业制定数据驱动的AI投资和应用路线图。"
        ),
        key_themes=[
            "AI技术市场分析",
            "企业应用场景",
            "数字化转型挑战",
            "实施策略与路线图",
            "风险管理与合规"
        ],
        estimated_total_words=8000,
        sections=[
            create_test_chapter_outline_1(),
            create_test_chapter_outline_2(),
        ]
    )


# ==================== 测试用例 ====================

@pytest.mark.asyncio
async def test_chapter_researcher_case_1():
    """
    测试用例1：测试AI市场分析章节的研究能力
    验证能否生成高质量的搜索查询并获取研究结果
    """
    logger.info("=" * 80)
    logger.info("测试用例1：AI技术市场现状与趋势 - 研究节点测试")
    logger.info("=" * 80)

    # 构建测试状态
    test_state = {
        "chapter_id": 1,
        "document_outline": create_test_document_outline(),
        "chapter_outline": create_test_chapter_outline_1(),
        "target_word_count": 1200,
    }

    # 执行研究节点
    result = await chapter_researcher(test_state)

    # 验证输出
    assert "synthesized_materials" in result, "缺少研究结果字段"
    assert isinstance(result["synthesized_materials"], str), "研究结果应该是字符串"
    assert len(result["synthesized_materials"]) > 100, "研究结果内容太少"

    logger.success(f"✅ 研究完成，获得素材长度: {len(result['synthesized_materials'])} 字符")
    logger.info("研究结果预览:")
    logger.info(result["synthesized_materials"][:500] + "...")

    return result


@pytest.mark.asyncio
async def test_chapter_researcher_case_2():
    """
    测试用例2：测试企业数字化转型章节的研究能力
    侧重案例和问题导向的研究
    """
    logger.info("=" * 80)
    logger.info("测试用例2：企业数字化转型挑战 - 研究节点测试")
    logger.info("=" * 80)

    # 构建测试状态
    test_state = {
        "chapter_id": 2,
        "document_outline": create_test_document_outline(),
        "chapter_outline": create_test_chapter_outline_2(),
        "target_word_count": 1000,
    }

    # 执行研究节点
    result = await chapter_researcher(test_state)

    # 验证输出
    assert "synthesized_materials" in result, "缺少研究结果字段"
    assert isinstance(result["synthesized_materials"], str), "研究结果应该是字符串"
    assert len(result["synthesized_materials"]) > 100, "研究结果内容太少"

    logger.success(f"✅ 研究完成，获得素材长度: {len(result['synthesized_materials'])} 字符")
    logger.info("研究结果预览:")
    logger.info(result["synthesized_materials"][:500] + "...")

    return result


@pytest.mark.asyncio
async def test_chapter_researcher_query_generation():
    """
    测试用例3：验证搜索查询生成的质量
    检查生成的查询是否符合要求（中文、具体、多样化）
    """
    logger.info("=" * 80)
    logger.info("测试用例3：搜索查询生成质量验证")
    logger.info("=" * 80)

    # 使用第一个测试章节
    test_state = {
        "chapter_id": 1,
        "document_outline": create_test_document_outline(),
        "chapter_outline": create_test_chapter_outline_1(),
        "target_word_count": 1200,
    }

    # 这里我们只测试查询生成部分
    # 需要手动检查日志输出中的查询质量
    logger.info("开始生成搜索查询...")

    result = await chapter_researcher(test_state)

    logger.info("请检查日志中的查询生成部分，验证:")
    logger.info("  ✓ 查询是否为中文")
    logger.info("  ✓ 查询是否具体且可搜索")
    logger.info("  ✓ 查询是否覆盖不同信息维度")
    logger.info("  ✓ 查询数量是否在 5-8 个范围内")

    return result


@pytest.mark.asyncio
async def test_chapter_researcher_optimized_search():
    """
    测试用例4：验证优化后的搜索策略
    验证：生成4个diverse查询，每个查询返回5个结果 = 总共20个网页
    重点检查查询的多样性和搜索结果的质量
    """
    logger.info("=" * 80)
    logger.info("测试用例4：优化后的搜索策略验证（4 diverse queries × 5 results）")
    logger.info("=" * 80)

    # 创建一个专门的测试章节，用于验证多样性
    test_chapter = Section(
        title="云计算技术发展现状与趋势",
        description=(
            "全面分析云计算技术在2024-2025年的发展状况，"
            "包括市场规模、技术架构演进、安全挑战和应用案例。"
        ),
        writing_guidance=(
            "采用多维度分析框架，从技术、市场、应用、安全等不同角度切入。"
            "每个维度需要独立的数据支撑和案例验证。"
        ),
        content_requirements=(
            "需要：(1) 全球云计算市场规模数据, "
            "(2) 主流云服务商技术对比, "
            "(3) 企业上云案例分析, "
            "(4) 云安全事件统计, "
            "(5) 行业专家对未来趋势的预测。"
        ),
        visual_elements=True,
        estimated_words=1500,
        writing_priority="high",
        subsections=[
            SubSection(
                sub_section_title="云计算市场规模与增长",
                description="分析全球和中国云计算市场的规模、增长率和竞争格局。",
                writing_guidance="使用权威机构数据，对比AWS、Azure、阿里云等主要厂商。",
                estimated_word_count=400
            ),
            SubSection(
                sub_section_title="云原生技术架构演进",
                description="探讨容器化、微服务、Serverless等云原生技术的发展。",
                writing_guidance="结合技术案例和架构图，说明技术演进路径。",
                estimated_word_count=500
            ),
            SubSection(
                sub_section_title="云安全挑战与应对",
                description="分析云环境下的安全风险和最佳实践。",
                writing_guidance="引用真实安全事件，提供可落地的安全建议。",
                estimated_word_count=400
            ),
            SubSection(
                sub_section_title="企业云迁移实践",
                description="分享典型企业的云迁移经验和教训。",
                writing_guidance="选择不同行业的代表性案例，提炼共性问题。",
                estimated_word_count=200
            ),
        ]
    )

    test_state = {
        "chapter_id": 100,
        "document_outline": create_test_document_outline(),
        "chapter_outline": test_chapter,
        "target_word_count": 1500,
    }

    logger.info("\n📋 测试目标:")
    logger.info("  ✓ 验证生成的查询数量是否为 4 个")
    logger.info("  ✓ 验证查询是否覆盖不同维度（市场/技术/安全/应用）")
    logger.info("  ✓ 验证每个查询返回约 5 个搜索结果")
    logger.info("  ✓ 验证总网页数约为 20 个（4×5）")
    logger.info("  ✓ 验证研究结果质量和多样性\n")

    # 执行研究节点
    result = await chapter_researcher(test_state)

    # 验证输出
    assert "synthesized_materials" in result, "缺少研究结果字段"
    assert isinstance(result["synthesized_materials"], str), "研究结果应该是字符串"
    assert len(result["synthesized_materials"]) > 500, "研究结果内容太少"

    # 统计结果
    materials = result["synthesized_materials"]
    logger.info("\n" + "=" * 80)
    logger.info("📊 搜索优化效果统计")
    logger.info("=" * 80)
    logger.success(f"✅ 研究素材总长度: {len(materials):,} 字符")

    # 检查是否包含多个主题的研究结果
    topic_count = materials.count("## Topic:")
    logger.info(f"📌 研究主题数量: {topic_count} 个")

    if topic_count == 4:
        logger.success("✅ 查询数量验证通过：恰好4个查询")
    elif topic_count < 4:
        logger.warning(f"⚠️  查询数量少于预期：{topic_count}/4")
    else:
        logger.warning(f"⚠️  查询数量多于预期：{topic_count}/4")

    # 预览研究结果
    logger.info("\n" + "=" * 80)
    logger.info("📖 研究结果预览（前800字符）")
    logger.info("=" * 80)
    logger.info(materials[:800] + "...\n")

    logger.info("💡 手动检查要点:")
    logger.info("  1. 查看日志中生成的4个查询是否覆盖不同维度")
    logger.info("  2. 每个查询的搜索结果是否为5个左右")
    logger.info("  3. 研究内容是否涵盖市场、技术、安全、应用等多个角度")
    logger.info("  4. 是否避免了大量重复信息")

    return result


@pytest.mark.asyncio
async def test_chapter_researcher_error_handling():
    """
    测试用例5：错误处理测试
    测试当章节大纲不完整时的容错能力
    """
    logger.info("=" * 80)
    logger.info("测试用例5：错误处理与容错能力测试")
    logger.info("=" * 80)

    # 创建一个最简化的章节大纲（缺少部分字段）
    minimal_chapter = Section(
        title="简化测试章节",
        description="这是一个用于测试错误处理的简化章节。",
        estimated_words=500,
        writing_priority="low",
        subsections=[]
    )

    test_state = {
        "chapter_id": 99,
        "document_outline": create_test_document_outline(),
        "chapter_outline": minimal_chapter,
        "target_word_count": 500,
    }

    # 执行研究节点 - 应该能够容错处理
    try:
        result = await chapter_researcher(test_state)
        assert "synthesized_materials" in result
        logger.success("✅ 错误处理测试通过：即使大纲简化，仍能完成研究")
    except Exception as e:
        logger.error(f"❌ 错误处理失败: {e}")
        raise

    return result


# ==================== 手动运行测试 ====================

async def run_all_tests():
    """
    手动运行所有测试（不使用 pytest）
    """
    logger.info("\n" + "=" * 80)
    logger.info("🧪 开始执行 Chapter Researcher 节点完整测试套件")
    logger.info("=" * 80 + "\n")

    tests = [
        ("AI市场分析章节研究", test_chapter_researcher_case_1),
        ("数字化转型章节研究", test_chapter_researcher_case_2),
        ("搜索查询质量验证", test_chapter_researcher_query_generation),
        ("优化搜索策略验证（4×5）", test_chapter_researcher_optimized_search),
        ("错误处理测试", test_chapter_researcher_error_handling),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            logger.info(f"\n🔬 运行测试: {test_name}")
            result = await test_func()
            results.append((test_name, "PASSED", result))
            logger.success(f"✅ {test_name} - 通过\n")
        except Exception as e:
            results.append((test_name, "FAILED", str(e)))
            logger.error(f"❌ {test_name} - 失败: {e}\n")

    # 打印测试总结
    logger.info("\n" + "=" * 80)
    logger.info("📊 测试结果汇总")
    logger.info("=" * 80)

    passed_count = sum(1 for _, status, _ in results if status == "PASSED")
    total_count = len(results)

    for test_name, status, _ in results:
        status_icon = "✅" if status == "PASSED" else "❌"
        logger.info(f"  {status_icon} {test_name}: {status}")

    logger.info("=" * 80)
    logger.info(f"总计: {passed_count}/{total_count} 测试通过")
    logger.info("=" * 80 + "\n")

    return results


if __name__ == "__main__":
    """
    直接运行此文件进行测试

    使用方法:
        python test/test_chapter_researcher.py

    或使用 pytest:
        pytest test/test_chapter_researcher.py -v -s
    """
    asyncio.run(run_all_tests())
