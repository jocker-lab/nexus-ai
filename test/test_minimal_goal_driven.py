# -*- coding: utf-8 -*-
"""
@File    :   test_minimal_goal_driven.py
@Time    :   2025/11/21
@Author  :   Claude
@Version :   1.0
@Desc    :   最小化Goal-Driven Summarization测试 - 3次搜索，观察summary质量
"""

import asyncio
import json
from loguru import logger
from dotenv import load_dotenv
import sys

load_dotenv()

from app.agents.core.agent_factory import create_goal_driven_deep_agent
from app.agents.tools.search import tavily_search
from app.agents.schemas.document_outline_schema import Section, SubSection


# ==================== 测试配置 ====================

# 3个精心挑选的搜索query
SEARCH_QUERIES = [
    "Tesla FSD自动驾驶软件版本 功能特性",  # Tesla FSD案例
    "2024年全球AI市场规模 Gartner IDC",   # 市场数据
    "特斯拉Model 3价格 配置 车型介绍",      # 噪音数据（应该被过滤）
]

# Chapter outline - 研究目标
TEST_CHAPTER = Section(
    title="自动驾驶技术发展报告",
    description="分析2024年自动驾驶技术的发展现状，重点关注软件系统的技术特性和市场数据。",
    content_requirements=(
        "需要收集：(1) Tesla FSD等主流自动驾驶软件的版本和功能特性, "
        "(2) 自动驾驶技术市场规模数据, "
        "(3) 技术发展趋势。"
    ),
    visual_elements=False,
    estimated_words=1000,
    writing_priority="high",
    subsections=[
        SubSection(
            sub_section_title="自动驾驶软件技术分析",
            description="重点分析Tesla FSD等主流软件的技术特性",
            writing_guidance="以功能和版本为主线，不要过多描述车型参数",
            estimated_word_count=500
        ),
    ]
)


# ==================== 搜索结果收集器 ====================

SEARCH_RESULTS = []  # 存储每次搜索的原始结果


def patch_search_to_collect_results():
    """Patch搜索函数，收集原始搜索结果"""
    import functools

    original_func = tavily_search.searcher.func

    @functools.wraps(original_func)
    def collecting_searcher(query: str):
        result = original_func(query)

        # 收集结果
        SEARCH_RESULTS.append({
            "query": query,
            "result": result,
            "length": len(result)
        })

        logger.info(f"🔍 Search #{len(SEARCH_RESULTS)}: {query}")
        logger.info(f"📄 Result length: {len(result)} chars")

        return result

    tavily_search.searcher.func = collecting_searcher
    logger.success("✅ Search result collector enabled")


# ==================== 主测试函数 ====================

async def test_minimal_goal_driven():
    """
    最小化测试：3次搜索 + 1次summarization

    测试流程：
    1. 创建agent（max_tokens_before_summary=8000，确保第3次搜索触发）
    2. 执行3次搜索
    3. 捕获summarization输出
    4. 保存原始搜索内容和summary到文件
    """
    logger.info("\n" + "🎯" * 50)
    logger.info("🎯 最小化Goal-Driven Summarization测试")
    logger.info("🎯 3次搜索 → 第3次触发总结")
    logger.info("🎯" * 50 + "\n")

    # 启用搜索结果收集
    patch_search_to_collect_results()

    # 创建agent（降低阈值以确保第3次搜索触发summarization）
    logger.info("🤖 Creating Goal-Driven Agent with LOW threshold...")

    # 使用DeepSeek模型
    from langchain_openai import ChatOpenAI
    from app.config import settings

    deepseek_model = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=settings.DEEPSEEK_API_KEY,
        openai_api_base="https://api.deepseek.com",
        max_tokens=8000,
        temperature=0.3,
    )

    system_prompt = f"""你是一个专业的研究助手。

研究任务：{TEST_CHAPTER.title}
研究目标：{TEST_CHAPTER.description}
内容需求：{TEST_CHAPTER.content_requirements}

请依次执行用户的搜索指令。"""

    agent = create_goal_driven_deep_agent(
        model=deepseek_model,  # 使用DeepSeek
        system_prompt=system_prompt,
        tools=[tavily_search.searcher],
        use_goal_driven_summarization=True,
        max_tokens_before_summary=8000,  # 🔥 降低到8000，确保第3次搜索触发
        messages_to_keep=1,              # 只保留最近1条消息
    )

    logger.success("✅ Agent created")
    logger.info(f"   Threshold: 8000 tokens")
    logger.info(f"   Messages to keep: 1")
    logger.info("")

    # 初始state
    state = {
        "messages": [],
        "chapter_outline": TEST_CHAPTER,
    }

    # 执行3次搜索
    logger.info("🔍 Starting 3 searches...")
    logger.info("=" * 100)

    for i, query in enumerate(SEARCH_QUERIES, 1):
        logger.info(f"\n{'='*100}")
        logger.info(f"📝 SEARCH #{i}: {query}")
        logger.info(f"{'='*100}")

        # 调用agent
        result = await agent.ainvoke({
            **state,
            "messages": state["messages"] + [
                {"role": "user", "content": f"请搜索：{query}"}
            ]
        })

        # 更新state
        state = {
            "messages": result.get("messages", []),
            "chapter_outline": TEST_CHAPTER,
        }

        # 检查是否有summary
        messages = state["messages"]
        for msg in messages:
            if hasattr(msg, "content") and "总结" in str(msg.content):
                logger.warning(f"🔄 SUMMARY DETECTED after search #{i}!")

        logger.info(f"✅ Search #{i} completed")
        logger.info(f"   Current messages: {len(state['messages'])}")

    logger.info("\n" + "=" * 100)
    logger.info("✅ All 3 searches completed")
    logger.info("=" * 100)

    # 提取summary（查找HumanMessage中包含"总结"的内容）
    summary = None
    for msg in state["messages"]:
        if hasattr(msg, "content") and "summary" in str(msg.content).lower():
            summary = msg.content
            break
        elif hasattr(msg, "content") and "总结" in str(msg.content):
            summary = msg.content
            break

    if not summary:
        # 尝试在所有消息中找包含"研究"的HumanMessage
        for msg in state["messages"]:
            if msg.__class__.__name__ == "HumanMessage" and len(str(msg.content)) > 200:
                summary = msg.content
                break

    # 保存结果到文件
    output = {
        "test_info": {
            "chapter_title": TEST_CHAPTER.title,
            "research_objective": TEST_CHAPTER.description,
            "content_requirements": TEST_CHAPTER.content_requirements,
            "total_searches": len(SEARCH_QUERIES),
        },
        "search_results": SEARCH_RESULTS,
        "summary": summary,
    }

    # 保存JSON
    output_file = "/test_output/logs/minimal_test_comparison.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logger.success(f"✅ Results saved to: {output_file}")

    # 保存易读版本
    readable_file = "/test_output/logs/minimal_test_comparison.txt"
    with open(readable_file, "w", encoding="utf-8") as f:
        f.write("=" * 100 + "\n")
        f.write("Goal-Driven Summarization 质量对比测试\n")
        f.write("=" * 100 + "\n\n")

        f.write("【研究目标】\n")
        f.write(f"章节标题：{TEST_CHAPTER.title}\n")
        f.write(f"研究目标：{TEST_CHAPTER.description}\n")
        f.write(f"内容需求：{TEST_CHAPTER.content_requirements}\n")
        f.write("\n" + "=" * 100 + "\n\n")

        for i, sr in enumerate(SEARCH_RESULTS, 1):
            f.write(f"【搜索 #{i}】\n")
            f.write(f"Query: {sr['query']}\n")
            f.write(f"长度: {sr['length']} 字符\n")
            f.write(f"\n结果内容:\n")
            f.write("-" * 100 + "\n")
            f.write(sr['result'][:2000] + "...\n")  # 只保存前2000字符
            f.write("-" * 100 + "\n\n")

        f.write("=" * 100 + "\n")
        f.write("【Goal-Driven Summary】\n")
        f.write("=" * 100 + "\n")
        if summary:
            f.write(summary)
        else:
            f.write("⚠️ 未检测到summary（可能summarization未触发）")
        f.write("\n\n")

    logger.success(f"✅ Readable version saved to: {readable_file}")

    # 打印summary预览
    logger.info("\n" + "🔍" * 50)
    logger.info("📋 SUMMARY PREVIEW:")
    logger.info("🔍" * 50)
    if summary:
        logger.info(summary[:500] + "...")
    else:
        logger.warning("⚠️ No summary detected")
    logger.info("🔍" * 50 + "\n")

    return output


if __name__ == "__main__":
    """
    运行方式：
        python test/test_minimal_goal_driven.py 2>&1 | tee logs/minimal_test.log
    """

    # 配置loguru
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

    # 运行测试
    asyncio.run(test_minimal_goal_driven())
