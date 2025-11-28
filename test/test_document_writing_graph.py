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
    title="人工智能技术发展报告",
    language="zh",
    target_audience="技术管理者、AI研究人员、投资决策者",
    writing_style="business",
    writing_tone="authoritative",
    writing_purpose="为读者提供AI技术发展的全面视角，包括技术趋势、应用案例和未来展望",
    key_themes=[
        "大模型技术演进",
        "AI商业应用实践",
    ],
    estimated_total_words=3000,
    sections=[
        Section(
            title="第一章 大模型技术现状",
            description="分析当前大语言模型的技术发展现状、核心突破和主流架构",
            writing_guidance="采用技术演进的时间线视角，从架构创新到模型对比到训练技术，层层递进。",
            content_requirements="需要包含：1) Transformer架构演进脉络 2) 主流模型的参数规模和性能对比数据",
            visual_elements=False,
            estimated_words=1500,
            writing_priority="high",
            subsections=[
                SubSection(
                    sub_section_title="Transformer架构演进",
                    description="追溯Transformer从诞生到现在的技术演进路径",
                    writing_guidance="""
                    【段落1 - 起源与突破】(150-200字)
                    - 从2017年原始论文切入，说明Transformer的革命性意义
                    - 简述其替代RNN/LSTM成为主流架构的核心原因
                    - 点明自注意力机制(Self-Attention)解决的关键问题

                    【段落2 - 核心机制解析】(250-300字)
                    - 详细解释Multi-Head Attention的工作原理和价值
                    - 说明位置编码(Positional Encoding)在序列建模中的作用

                    【段落3 - 关键优化演进】(200-250字)
                    - 按时间线梳理主要改进方向
                    """,
                    estimated_word_count=650
                ),
                SubSection(
                    sub_section_title="主流模型性能对比",
                    description="对比GPT系列、Claude、LLaMA等主流模型",
                    writing_guidance="""
                    【段落1 - 模型概览与分类】(200-250字)
                    - 列举当前市场主流大模型

                    【段落2 - 综合能力基准测试】(350-400字)
                    - 介绍MMLU作为最权威的综合评测基准
                    """,
                    estimated_word_count=900
                ),
            ]
        ),

        Section(
            title="第二章 AI商业应用实践",
            description="深入分析AI技术在各行业的落地应用案例",
            writing_guidance="以实际案例为主导，采用'行业背景-痛点分析-解决方案-效果评估'的四段式结构。",
            content_requirements="需要包含：1) 3个不同行业的深度案例 2) 每个案例的ROI数据",
            visual_elements=True,
            estimated_words=1500,
            writing_priority="high",
            subsections=[
                SubSection(
                    sub_section_title="金融行业：智能风控与客服",
                    description="分析AI在银行、保险等金融机构的应用",
                    writing_guidance="""
                    【段落1 - 行业背景与痛点】(150-180字)
                    - 描述金融行业面临的核心挑战

                    【段落2 - AI解决方案】(280-320字)
                    - 分两个应用场景展开：风控应用和智能客服
                    """,
                    estimated_word_count=650
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
