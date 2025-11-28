# -*- coding: utf-8 -*-
"""
@File    :   test_research_subgraph.py
@Time    :   2025/11/21
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   Research Subgraph 测试案例
"""

import asyncio
from datetime import datetime
from loguru import logger
from app.agents.core.publisher.subgraphs.research.agent import build_research_subgraph, run_research_subgraph
from dotenv import load_dotenv

load_dotenv()


def create_test_state():
    """
    创建测试用的初始状态
    """
    # 创建研究任务列表
    research_topics = [
        "2024年大语言模型技术发展现状",
        "Transformer架构的最新优化技术",
        "开源大模型与闭源大模型的性能对比",
    ]

    initial_state = {
        "language": "zh-CN",
        "research_topics": research_topics,
        "need_search": True,
        "results": []
    }

    return initial_state


async def test_research_subgraph():
    """
    测试 Research Subgraph 的完整流程
    """
    logger.info("=" * 70)
    logger.info("🧪 开始测试 Research Subgraph")
    logger.info(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70 + "\n")

    # 1. 创建测试状态
    logger.info("📝 步骤 1/3: 创建测试状态...")
    initial_state = create_test_state()
    logger.info(f"   ✓ 语言设置: {initial_state['language']}")
    logger.info(f"   ✓ 研究主题数: {len(initial_state['research_topics'])}")
    logger.info(f"   ✓ 是否需要搜索: {initial_state['need_search']}")
    for i, topic in enumerate(initial_state['research_topics'], 1):
        logger.info(f"      {i}. {topic}")
    logger.info("")

    # 2. 构建 Subgraph
    logger.info("🏗️  步骤 2/3: 构建 Research Subgraph...")
    try:
        research_graph = build_research_subgraph()
        logger.info("   ✓ Subgraph 构建成功\n")
    except Exception as e:
        logger.error(f"   ✗ Subgraph 构建失败: {e}")
        raise

    # 3. 执行 Subgraph
    logger.info("🚀 步骤 3/3: 执行 Research 流程...")
    logger.info("   节点执行顺序: dispatch → execute_single_research (并行) → aggregate\n")

    try:
        # 异步调用
        result = await research_graph.ainvoke(initial_state)

        logger.info("\n" + "=" * 70)
        logger.info("✅ Research Subgraph 执行完成!")
        logger.info("=" * 70 + "\n")

        # 4. 验证结果
        logger.info("📊 执行结果验证:")

        # 检查必须的字段
        assert "results" in result, "缺少 results 字段"
        assert "research_draft" in result, "缺少 research_draft 字段"

        results = result["results"]
        research_draft = result["research_draft"]

        # 验证研究结果
        assert len(results) == len(initial_state['research_topics']), \
            f"结果数量不匹配: 期望 {len(initial_state['research_topics'])}, 实际 {len(results)}"

        # 打印关键指标
        logger.info(f"   ✓ 总任务数: {len(results)}")

        success_count = sum(1 for r in results if r.get("success", False))
        logger.info(f"   ✓ 成功任务: {success_count}/{len(results)}")

        # 打印每个任务的结果
        for i, result_item in enumerate(results, 1):
            topic = result_item.get("topic", "Unknown")
            success = result_item.get("success", False)
            result_length = len(result_item.get("result", ""))
            status = "✅" if success else "❌"
            logger.info(f"   {status} 任务 {i}: {topic} (结果长度: {result_length} 字符)")

        # 打印最终草稿预览
        draft_preview = research_draft[:300].replace('\n', ' ')
        logger.info(f"   ✓ 研究草稿预览: {draft_preview}...")
        logger.info(f"   ✓ 研究草稿总长度: {len(research_draft)} 字符")

        logger.info("\n" + "=" * 70)
        logger.success("🎉 所有测试通过！Research Subgraph 运行正常")
        logger.info("=" * 70)

        return result

    except Exception as e:
        logger.error("\n" + "=" * 70)
        logger.error(f"❌ 测试失败: {str(e)}")
        logger.error("=" * 70)
        import traceback
        traceback.print_exc()
        raise


async def test_convenience_function():
    """
    测试便捷函数 run_research_subgraph
    """
    logger.info("\n" + "=" * 70)
    logger.info("🧪 测试便捷函数 run_research_subgraph")
    logger.info("=" * 70 + "\n")

    topics = [
        "Python异步编程最佳实践",
        "LangGraph状态管理机制",
    ]

    logger.info("📝 测试参数:")
    logger.info(f"   ✓ 主题数: {len(topics)}")
    for i, topic in enumerate(topics, 1):
        logger.info(f"      {i}. {topic}")
    logger.info("")

    try:
        result = await run_research_subgraph(
            topics=topics,
            need_search=True,
            language="zh-CN"
        )

        logger.info("✅ 便捷函数执行成功")
        logger.info(f"   ✓ 结果类型: {type(result)}")

        # 注意：run_research_subgraph 返回的是 final_result 字段
        # 但代码中实际返回的是 research_draft
        if isinstance(result, dict):
            if "research_draft" in result:
                logger.info(f"   ✓ 研究草稿长度: {len(result['research_draft'])} 字符")
            elif "final_result" in result:
                logger.info(f"   ✓ 最终结果长度: {len(result['final_result'])} 字符")
        else:
            logger.info(f"   ✓ 结果长度: {len(result)} 字符")

        logger.success("🎉 便捷函数测试通过！")
        return result

    except Exception as e:
        logger.error(f"❌ 便捷函数测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


async def test_individual_nodes():
    """
    测试各个节点的独立功能（可选）
    """
    logger.info("\n" + "=" * 70)
    logger.info("🔍 节点独立测试（可选）")
    logger.info("=" * 70 + "\n")

    from app.agents.core.publisher.subgraphs.research.nodes import (
        plan_research,
        execute_single_research_node,
        aggregate_results
    )

    initial_state = create_test_state()

    # 测试 1: plan_research
    logger.info("1️⃣ 测试 plan_research...")
    try:
        dispatch_result = plan_research(initial_state)
        # plan_research 返回 Command(goto=sends)
        logger.info(f"   ✓ 类型: {type(dispatch_result)}")
        logger.success("   ✓ plan_research 测试通过")
    except Exception as e:
        logger.error(f"   ✗ plan_research 测试失败: {e}")

    # 测试 2: execute_single_research_node
    logger.info("2️⃣ 测试 execute_single_research_node...")
    try:
        # 创建单任务状态
        single_state = {
            "language": "zh-CN",
            "current_research_topic": "测试主题：LangGraph基础概念",
            "need_search": True
        }
        single_result = await execute_single_research_node(single_state)
        assert "results" in single_result, "缺少 results 字段"
        assert len(single_result["results"]) == 1, "results 应该包含一个结果"
        result_item = single_result["results"][0]
        assert "topic" in result_item, "结果缺少 topic 字段"
        assert "result" in result_item, "结果缺少 result 字段"
        assert "success" in result_item, "结果缺少 success 字段"
        logger.info(f"   ✓ 主题: {result_item['topic']}")
        logger.info(f"   ✓ 成功: {result_item['success']}")
        logger.info(f"   ✓ 结果长度: {len(result_item['result'])} 字符")
        logger.success("   ✓ execute_single_research_node 测试通过")
    except Exception as e:
        logger.error(f"   ✗ execute_single_research_node 测试失败: {e}")
        import traceback
        traceback.print_exc()

    # 测试 3: aggregate_results
    logger.info("3️⃣ 测试 aggregate_results...")
    try:
        # 模拟已收集的结果
        aggregate_state = {
            **initial_state,
            "results": [
                {
                    "topic": "测试主题1",
                    "result": "这是第一个研究结果。",
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "topic": "测试主题2",
                    "result": "这是第二个研究结果。",
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        aggregate_result = aggregate_results(aggregate_state)
        assert "research_draft" in aggregate_result, "缺少 research_draft 字段"
        logger.info(f"   ✓ 研究草稿长度: {len(aggregate_result['research_draft'])} 字符")
        logger.success("   ✓ aggregate_results 测试通过")
    except Exception as e:
        logger.error(f"   ✗ aggregate_results 测试失败: {e}")

    logger.info("\n" + "=" * 70)
    logger.info("节点独立测试完成")
    logger.info("=" * 70)


async def test_without_search():
    """
    测试不使用搜索工具的情况
    """
    logger.info("\n" + "=" * 70)
    logger.info("🧪 测试不使用搜索工具的情况")
    logger.info("=" * 70 + "\n")

    topics = ["Python编程基础", "数据结构与算法"]

    logger.info("📝 测试参数:")
    logger.info(f"   ✓ 主题数: {len(topics)}")
    logger.info(f"   ✓ 使用搜索: False")
    for i, topic in enumerate(topics, 1):
        logger.info(f"      {i}. {topic}")
    logger.info("")

    try:
        research_graph = build_research_subgraph()

        initial_state = {
            "language": "zh-CN",
            "research_topics": topics,
            "need_search": False,
            "results": []
        }

        result = await research_graph.ainvoke(initial_state)

        logger.info("✅ 测试完成")
        logger.info(f"   ✓ 结果数: {len(result['results'])}")
        logger.success("🎉 不使用搜索工具的测试通过！")

        return result

    except Exception as e:
        logger.error(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # 运行完整流程测试
    logger.info("开始运行 Research Subgraph 测试套件\n")

    # 测试 1: 完整流程
    result = asyncio.run(test_research_subgraph())

    # # 测试 2: 便捷函数
    # asyncio.run(test_convenience_function())

    # # 测试 3: 节点独立测试（可选）
    # asyncio.run(test_individual_nodes())

    # 测试 4: 不使用搜索（可选）
    # asyncio.run(test_without_search())

    logger.info("\n" + "=" * 80)
    logger.success("🎊 所有测试套件执行完成！")
    logger.info("=" * 80)
