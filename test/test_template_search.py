# -*- coding: utf-8 -*-
"""
测试模版搜索相似度
"""
import asyncio
import sys
sys.path.insert(0, "/Users/seanxiao/PycharmProjects/nexus-ai")

from app.service.template_service import search_templates


async def test_search():
    queries = [
        "请帮我生成一份关于克罗恩病与短肠综合征的病例报告",
        "克罗恩病病历模版",
        "炎症性肠病患者的电子病历",
        "帮我写一份医疗病历报告",
        "短肠综合征营养评估",
    ]

    print("=" * 60)
    print("模版搜索相似度测试")
    print("=" * 60)

    for query in queries:
        print(f"\n📝 查询: {query}")
        print("-" * 40)

        results = await search_templates(
            query_text=query,
            top_k=5,
            threshold=0.0  # 不过滤，看所有结果
        )

        if not results:
            print("   ❌ 未找到任何结果")
            continue

        for r in results:
            score = r['similarity_score']
            title = r['title']

            # 标记不同阈值
            if score >= 0.8:
                marker = "🟢 (>0.8 自动选择)"
            elif score >= 0.5:
                marker = "🟡 (>0.5 可匹配)"
            else:
                marker = "🔴 (<0.5 低相似)"

            print(f"   {score:.2%} - {title} {marker}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(test_search())
