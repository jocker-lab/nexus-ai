# -*- coding: utf-8 -*-
"""
@File    :   test_document_writing_graph.py
@Time    :   2025/11/18 10:15
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   Document Writing Graph 完整测试
"""

import asyncio
from loguru import logger

from app.agents.schemas.document_outline_schema import DocumentOutline, Section, SubSection
from app.agents.core.publisher.writing.agent import create_main_graph
from app.agents.core.publisher.writing.state import DocumentState
from dotenv import load_dotenv

load_dotenv()


# ========== 测试数据 ==========

document_outline = DocumentOutline(
    title="2025年第一季度中原银行风险分析报告",
    language="zh",
    target_audience="公司高管层、董事会成员、风险管理委员会、监管机构",
    writing_style="business",
    writing_tone="authoritative",
    writing_purpose="全面评估中原银行2025年第一季度的经营状况与风险水平，重点分析同业竞争地位及个人业务风险，为管理决策提供依据。",
    key_themes=[
        "宏观环境与监管动态",
        "经营业绩与同业对标",
        "个人信贷业务风险特征",
        "风险抵御能力评估",
        "战略建议与展望",
    ],
    estimated_total_words=8000,
    sections=[
        Section(
            title="一、宏观环境与监管政策",
            description="分析2025年第一季度外部环境对银行经营的影响",
            writing_guidance="简明扼要地扫描宏观经济指标和核心监管政策，重点突出对区域性银行的影响。",
            content_requirements="包含GDP、利率环境、河南区域经济以及最新监管导向。",
            visual_elements=False,
            estimated_words=1200,
            writing_priority="medium",
            subsections=[
                SubSection(
                    sub_section_title="（一）宏观经济运行态势",
                    description="分析国内外经济走势及区域经济特点",
                    writing_guidance="重点分析利率下行趋势对息差的影响，以及河南区域经济的复苏情况。",
                    estimated_word_count=600
                ),
                SubSection(
                    sub_section_title="（二）监管政策导向",
                    description="梳理对中小银行影响重大的监管政策",
                    writing_guidance="关注资本新规、消费者权益保护以及防范化解金融风险的政策要求。",
                    estimated_word_count=600
                ),
            ]
        ),

        Section(
            title="二、报告期内经营概况",
            description="回顾2025年第一季度的整体经营业绩",
            writing_guidance="用数据说话，展示资产负债规模、营收利润以及资产质量的总体情况。",
            content_requirements="总资产、净利润、不良率等核心指标的同比环比变化。",
            visual_elements=True,
            estimated_words=1500,
            writing_priority="medium",
            subsections=[
                SubSection(
                    sub_section_title="（一）主要财务指标分析",
                    description="分析规模与效益指标",
                    writing_guidance="分析营收结构、净息差变化及成本收入比。",
                    estimated_word_count=800
                ),
                SubSection(
                    sub_section_title="（二）资产质量总体概览",
                    description="概述全行资产质量状况",
                    writing_guidance="简述不良贷款率、拨备覆盖率的变化，为后续详细风险分析做铺垫。",
                    estimated_word_count=700
                ),
            ]
        ),

        Section(
            title="三、同业对标分析",
            description="将本行关键指标与同类型上市城商行进行深度对标",
            writing_guidance="选取3-5家资产规模相近或区域类似的上市城商行作为标杆，找出差距与优势。数据需详实。",
            content_requirements="规模指标排名、盈利能力对比（ROE、ROA、净息差）、资产质量对比（不良率、拨备覆盖率）。",
            visual_elements=True,
            estimated_words=2000,
            writing_priority="high",
            subsections=[
                SubSection(
                    sub_section_title="（一）规模与市场地位对标",
                    description="对比资产负债规模及市场份额",
                    writing_guidance="""
                    【段落1】选取郑州银行、长沙银行、贵阳银行等作为对标对象。
                    【段落2】对比总资产增速、存贷款市场份额变化。
                    【可视化】生成'可比同业资产规模对比柱状图'。
                    """,
                    estimated_word_count=600
                ),
                SubSection(
                    sub_section_title="（二）盈利能力与效率对标",
                    description="对比营收增速、利润水平及运营效率",
                    writing_guidance="""
                    【段落1】深入分析净息差（NIM）与同业的差距，寻找原因（负债成本或资产收益）。
                    【段落2】对比中间业务收入占比，评估收入多元化程度。
                    【可视化】生成'同业净息差与ROE对比散点图'。
                    """,
                    estimated_word_count=700
                ),
                SubSection(
                    sub_section_title="（三）风险抵补能力对标",
                    description="对比资产质量核心指标",
                    writing_guidance="""
                    【段落1】对比不良贷款率和关注类贷款占比，评估资产质量的相对水平。
                    【段落2】对比拨备覆盖率和资本充足率，评估风险抵御的安全垫厚度。
                    """,
                    estimated_word_count=700
                ),
            ]
        ),

        Section(
            title="四、个人风险分析",
            description="深入聚焦个人零售信贷业务的风险状况",
            writing_guidance="针对个人住房贷款、个人经营贷和信用卡业务进行细分风险分析，关注客群信用变化。",
            content_requirements="个人贷款不良率、按揭贷款逾期情况、信用卡风险暴露、风控措施有效性。",
            visual_elements=True,
            estimated_words=2000,
            writing_priority="high",
            subsections=[
                SubSection(
                    sub_section_title="（一）个人信贷资产质量",
                    description="整体评估零售贷款的风险状况",
                    writing_guidance="""
                    【段落1】分析个人贷款整体不良率及五级分类迁徙情况。
                    【段落2】分析不同产品（房贷、消费贷、经营贷）的风险贡献度。
                    【可视化】生成'个人贷款各产品不良率趋势图'。
                    """,
                    estimated_word_count=600
                ),
                SubSection(
                    sub_section_title="（二）重点产品风险剖析",
                    description="聚焦按揭与信用卡两大核心产品",
                    writing_guidance="""
                    【段落1 - 住房按揭】分析'保交楼'背景下的按揭逾期风险及房价波动影响。
                    【段落2 - 信用卡】分析信用卡透支不良率、早期催收回款率及共债风险。
                    """,
                    estimated_word_count=800
                ),
                SubSection(
                    sub_section_title="（三）个人风险管控措施",
                    description="评估零售风控体系的有效性",
                    writing_guidance="""
                    【段落1】介绍大数据风控模型（如A/B/C卡）的迭代与应用。
                    【段落2】说明催收管理的优化措施及消费者权益保护执行情况。
                    """,
                    estimated_word_count=600
                ),
            ]
        ),

        Section(
            title="五、总结与建议",
            description="全篇总结并提出管理建议",
            writing_guidance="高度概括报告核心发现，提出针对性、可落地的战略建议。",
            content_requirements="经营综述、针对同业差距的改进建议、针对个人风险的管控建议。",
            visual_elements=False,
            estimated_words=1300,
            writing_priority="medium",
            subsections=[
                SubSection(
                    sub_section_title="（一）经营与风险综述",
                    description="总结报告期内核心观点",
                    writing_guidance="概括第一季度经营亮点、同业竞争地位变化及主要风险挑战。",
                    estimated_word_count=500
                ),
                SubSection(
                    sub_section_title="（二）管理改进建议",
                    description="基于分析提出的具体措施",
                    writing_guidance="""
                    【建议1】针对同业对标：如何提升息差韧性、优化负债成本。
                    【建议2】针对个人风险：建议加强数字化风控、优化客群结构。
                    【建议3】总体战略：关于资本补充与数字化转型的建议。
                    """,
                    estimated_word_count=800
                ),
            ]
        ),
    ]
)
# ========== 测试函数 ==========

async def test_document_writing_graph():
    """
    测试完整的 Document Writing Graph

    流程：
    1. 创建初始 state
    2. 编译 Main Graph
    3. 执行 graph
    4. 验证结果
    """
    logger.info("\n" + "="*80)
    logger.info("开始测试 Document Writing Graph")
    logger.info("="*80 + "\n")

    # === 1. 准备测试数据 ===
    logger.info("📋 [1/5] 准备测试数据...")

    # 计算目标总字数
    target_length = document_outline.estimated_total_words

    logger.info(f"  ↳ 文档标题: {document_outline.title}")
    logger.info(f"  ↳ 章节数量: {len(document_outline.sections)}")
    logger.info(f"  ↳ 目标总字数: {target_length}")
    logger.info(f"  ↳ 写作风格: {document_outline.writing_style}")
    logger.info(f"  ↳ 语言: {document_outline.language}\n")

    # === 2. 创建初始状态 ===
    logger.info("🔧 [2/5] 创建初始状态...")

    initial_state: DocumentState = {
        "chat_id": "test-chat-001",
        "document_id": "test-doc-001",
        "document_outline": document_outline,
    }

    logger.info("  ✓ 初始状态创建完成\n")

    # === 3. 编译 Main Graph ===
    logger.info("🏗️  [3/5] 编译 Main Graph...")

    try:
        main_graph = create_main_graph()
        logger.info("  ✓ Main Graph 编译成功\n")
    except Exception as e:
        logger.error(f"  ❌ Main Graph 编译失败: {e}")
        raise

    # === 4. 执行 Graph ===
    logger.info("🚀 [4/5] 执行 Document Writing Graph...")
    logger.info("  (这可能需要几分钟，请耐心等待...)\n")

    import time
    start_time = time.time()

    try:
        # 执行 graph
        result = await main_graph.ainvoke(initial_state)

        end_time = time.time()
        execution_time = end_time - start_time

        logger.info(f"\n  ✓ Graph 执行完成 (耗时: {execution_time:.2f}秒)\n")

    except Exception as e:
        logger.error(f"  ❌ Graph 执行失败: {e}", exc_info=True)
        raise

    # === 5. 验证结果 ===
    logger.info("✅ [5/5] 验证结果...")

    try:
        # 检查 completed_chapters
        assert "completed_chapters" in result, "缺少 completed_chapters"
        completed_chapters = result["completed_chapters"]
        expected_count = len(document_outline.sections)
        logger.info(f"  ✓ 完成章节数: {len(completed_chapters)}/{expected_count}")

        # 检查所有章节都完成
        expected_chapter_ids = set(range(1, expected_count + 1))
        actual_chapter_ids = set(completed_chapters.keys())
        assert expected_chapter_ids == actual_chapter_ids, f"章节ID不匹配: 期望 {expected_chapter_ids}, 实际 {actual_chapter_ids}"

        # 检查每个章节的结构
        for ch_id, ch_data in completed_chapters.items():
            assert "content" in ch_data, f"章节 {ch_id} 缺少 content"
            assert "metadata" in ch_data, f"章节 {ch_id} 缺少 metadata"
            logger.info(f"  ✓ 章节 {ch_id}: {len(ch_data['content'])} 字符, 评分: {ch_data['metadata'].get('final_score', 'N/A')}")

        # 检查 document_metadata
        assert "document_metadata" in result, "缺少 document_metadata"
        metadata = result["document_metadata"]
        logger.info(f"  ✓ 总字数: {metadata.get('total_words', 0)}")
        logger.info(f"  ✓ 平均评分: {metadata.get('avg_score', 0)}")

        # 检查 document (整合后文档)
        assert "document" in result, "缺少 document"
        document = result["document"]
        assert len(document) > 0, "document 为空"
        logger.info(f"  ✓ 最终文档长度: {len(document)} 字符")

        # 检查 document_review
        assert "document_review" in result, "缺少 document_review"
        review = result["document_review"]
        logger.info(f"  ✓ 审查状态: {review.get('status', 'N/A')}")
        logger.info(f"  ✓ 整体评估: {review.get('overall_assessment', 'N/A')}")

        logger.info("\n" + "="*80)
        logger.success("✅ 所有测试通过！")
        logger.info("="*80 + "\n")

        # === 6. 输出最终文档预览 ===
        logger.info("📄 最终文档预览 (前500字符):\n")
        logger.info("-"*80)
        logger.info(document[:500] + "...\n")
        logger.info("-"*80 + "\n")

        return result

    except AssertionError as e:
        logger.error(f"  ❌ 验证失败: {e}")
        raise
    except Exception as e:
        logger.error(f"  ❌ 验证过程出错: {e}", exc_info=True)
        raise


async def test_individual_nodes():
    """
    测试各个独立节点

    用于调试和验证单个节点的功能
    """
    logger.info("\n" + "="*80)
    logger.info("开始测试独立节点")
    logger.info("="*80 + "\n")

    from app.agents.core.publisher.writing.nodes import (
        chapter_dispatcher,
        chapter_aggregator,
        document_integrator,
        document_reviewer
    )

    # 创建基础 state
    base_state: DocumentState = {
        "chat_id": "test-chat-002",
        "document_id": "test-doc-002",
        "document_outline": document_outline,
        "writer_role": "技术分析师",
        "writer_profile": "专注于AI和科技领域的资深分析师",
        "writing_principles": ["准确性", "客观性", "前瞻性"],
        "completed_chapters": {},
        "document_metadata": {},
        "document_review": {},
        "document": "",
    }

    # === 测试 1: chapter_dispatcher ===
    logger.info("🧪 测试 chapter_dispatcher...")
    try:
        dispatcher_result = chapter_dispatcher(base_state)
        logger.info(f"  ✓ dispatcher 返回类型: {type(dispatcher_result)}")
        logger.success("  ✓ chapter_dispatcher 测试通过\n")
    except Exception as e:
        logger.error(f"  ❌ chapter_dispatcher 测试失败: {e}\n")

    # === 测试 2: chapter_aggregator ===
    logger.info("🧪 测试 chapter_aggregator...")
    try:
        # 模拟已完成的章节 (新结构，字段名与 merger_node 一致)
        aggregator_state = {
            **base_state,
            "completed_chapters": {
                1: {
                    "content": "# 第一章\n\n这是测试内容...",
                    "metadata": {
                        "chapter_id": 1,
                        "chapter_title": "第一章",
                        "word_count": 1200,
                        "revision_count": 1,
                        "final_score": 85,
                        "final_status": "pass",
                        "writer_role": "技术分析师",
                    }
                },
                2: {
                    "content": "# 第二章\n\n这是测试内容...",
                    "metadata": {
                        "chapter_id": 2,
                        "chapter_title": "第二章",
                        "word_count": 1300,
                        "revision_count": 0,
                        "final_score": 88,
                        "final_status": "pass",
                        "writer_role": "技术分析师",
                    }
                }
            }
        }

        aggregator_result = chapter_aggregator(aggregator_state)
        logger.info(f"  ✓ aggregator 返回 document_metadata: {aggregator_result.get('document_metadata')}")
        logger.success("  ✓ chapter_aggregator 测试通过\n")
    except Exception as e:
        logger.error(f"  ❌ chapter_aggregator 测试失败: {e}\n")
        aggregator_result = {}

    # === 测试 3: document_integrator ===
    logger.info("🧪 测试 document_integrator...")
    try:
        integrator_state = {
            **aggregator_state,
            "document_metadata": aggregator_result.get("document_metadata", {}),
        }

        integrator_result = await document_integrator(integrator_state)
        logger.info(f"  ✓ integrator 返回文档长度: {len(integrator_result.get('document', ''))}")
        logger.success("  ✓ document_integrator 测试通过\n")
    except Exception as e:
        logger.error(f"  ❌ document_integrator 测试失败: {e}\n")
        integrator_result = {}

    # === 测试 4: document_reviewer ===
    logger.info("🧪 测试 document_reviewer...")
    try:
        reviewer_state = {
            **integrator_state,
            "document": integrator_result.get("document", "# 测试文档\n\n这是测试内容..."),
        }

        reviewer_result = await document_reviewer(reviewer_state)
        latest_review = reviewer_result.get('latest_review')
        if latest_review:
            logger.info(f"  ✓ reviewer 返回审查状态: {latest_review.status}")
            logger.info(f"  ✓ reviewer 返回评分: {latest_review.score}")
            logger.info(f"  ✓ reviewer 返回建议数: {len(latest_review.actionable_suggestions)}")
        logger.info(f"  ✓ reviewer 修订次数: {reviewer_result.get('revision_count')}")
        logger.success("  ✓ document_reviewer 测试通过\n")
    except Exception as e:
        logger.error(f"  ❌ document_reviewer 测试失败: {e}\n")

    logger.info("="*80)
    logger.success("✅ 独立节点测试完成！")
    logger.info("="*80 + "\n")


# ========== 主函数 ==========

async def main():
    """主测试入口"""
    logger.info("\n" + "🎯 " + "="*74)
    logger.info("🎯  Document Writing Graph 测试套件")
    logger.info("🎯 " + "="*74 + "\n")

    # 选择测试模式
    test_mode = "full"  # 可选: "full", "nodes", "both"

    if test_mode in ["full", "both"]:
        logger.info("📌 运行完整 Graph 测试...\n")
        await test_document_writing_graph()

    if test_mode in ["nodes", "both"]:
        logger.info("📌 运行独立节点测试...\n")
        await test_individual_nodes()

    logger.info("\n" + "🎉 " + "="*74)
    logger.success("🎉  所有测试完成！")
    logger.info("🎉 " + "="*74 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
