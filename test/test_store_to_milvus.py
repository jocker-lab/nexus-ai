# -*- coding: utf-8 -*-
"""
测试 store_to_milvus 节点

流程：
1. 模拟一个 final_document
2. 调用 store_to_milvus 节点
3. 验证 Milvus 中数据是否存入
4. 测试向量搜索功能
"""

import asyncio
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# 模拟的测试文档
MOCK_FINAL_DOCUMENT = """
# 人工智能技术发展报告

## 第一章 大模型技术现状

### 1.1 Transformer架构演进

2017年，Google发布了具有里程碑意义的论文《Attention is All You Need》，首次提出了Transformer架构。这一架构彻底改变了自然语言处理领域的研究方向，其核心创新在于完全基于自注意力机制（Self-Attention）来建模序列数据，摒弃了传统的循环神经网络（RNN）和长短期记忆网络（LSTM）。

自注意力机制的核心优势在于能够直接建模序列中任意两个位置之间的依赖关系，无论它们之间的距离有多远。这解决了RNN在处理长序列时面临的梯度消失问题，同时也支持了并行计算，大幅提升了训练效率。

Multi-Head Attention是Transformer的核心组件，它将注意力机制分解为多个"头"，每个头独立学习不同的注意力模式。这种设计使模型能够同时关注不同位置的不同表示子空间，增强了模型的表达能力。

### 1.2 主流模型性能对比

当前市场上主流的大语言模型可以分为几个主要阵营：

1. **OpenAI GPT系列**：包括GPT-3.5和GPT-4，代表了闭源商业模型的最高水平
2. **Anthropic Claude系列**：以安全性和有用性著称，Claude 3已展现出强大的多模态能力
3. **Meta LLaMA系列**：开源社区的中坚力量，LLaMA 2和LLaMA 3推动了开源生态发展
4. **Google Gemini系列**：多模态原生设计，在视觉理解方面表现突出

在MMLU（Massive Multitask Language Understanding）基准测试中，GPT-4达到了86.4%的准确率，Claude 3 Opus紧随其后达到86.8%，而开源模型LLaMA 3 70B也达到了82%的水平。

## 第二章 AI商业应用实践

### 2.1 金融行业：智能风控与客服

金融行业面临的核心挑战包括：欺诈检测的实时性要求、信贷审批的效率与风险平衡、以及客户服务的24/7可用性需求。传统的规则引擎已难以应对日益复杂的欺诈手段和客户需求。

在智能风控领域，某股份制银行部署了基于大模型的实时反欺诈系统。该系统能够在50毫秒内完成交易风险评估，将欺诈识别准确率从92%提升至98.5%，误报率降低了60%。

在智能客服领域，AI客服机器人已能处理80%以上的常见咨询，包括账户查询、转账操作指引、产品介绍等。某银行的实践数据显示，引入AI客服后，人工客服的工作量减少了45%，客户满意度提升了12个百分点。

## 总结

人工智能技术正处于快速发展期，大模型技术的突破为各行业带来了前所未有的机遇。从技术层面看，Transformer架构的持续演进和模型规模的不断扩大推动了能力边界的拓展；从应用层面看，金融、医疗、制造等行业已经开始规模化落地AI解决方案。

未来，随着多模态能力的增强、推理成本的降低以及安全性的提升，AI技术将进一步深入各个领域，成为企业数字化转型的核心驱动力。
"""


async def test_store_to_milvus_node():
    """
    测试 store_to_milvus 节点的完整流程
    """
    logger.info("\n" + "=" * 60)
    logger.info("测试 store_to_milvus 节点")
    logger.info("=" * 60 + "\n")

    from app.agents.core.publisher.writing.nodes.store_to_milvus import store_to_milvus

    # 模拟 DocumentState
    mock_state = {
        "chat_id": "test-chat-milvus",
        "document_id": "",  # 将由 store_to_milvus 生成
        "final_document": MOCK_FINAL_DOCUMENT,
        # 其他必需字段
        "main_document_outline": None,
        "global_context": "",
        "global_glossary": {},
        "chapter_configs": [],
        "target_length": 3000,
        "completed_chapters": {},
        "quality_stats": {},
        "warnings": [],
        "integrated_document": "",
        "document_metadata": {},
        "global_review": {},
        "generation_time": 0.0,
    }

    logger.info("📄 测试文档长度: {} 字符".format(len(MOCK_FINAL_DOCUMENT)))
    logger.info("-" * 60)

    try:
        # 执行 store_to_milvus 节点
        result = await store_to_milvus(mock_state)

        document_id = result.get("document_id", "")

        if document_id:
            logger.success(f"\n✅ 存储成功！document_id: {document_id}")
            return document_id
        else:
            logger.error("\n❌ 存储失败：未返回 document_id")
            return None

    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_milvus_query(document_id: str):
    """
    测试从 Milvus 查询刚存入的数据
    """
    logger.info("\n" + "=" * 60)
    logger.info("测试 Milvus 查询")
    logger.info("=" * 60 + "\n")

    from app.client.milvus_client import get_milvus_client

    try:
        client = get_milvus_client()
        client.connect()
        client.create_collection()

        # 1. 检查 uuid 是否存在
        logger.info(f"🔍 检查 uuid 是否存在: {document_id}")
        exists = client.exists(document_id)
        logger.info(f"  ↳ 存在: {exists}")

        if exists:
            logger.success("✅ 数据确认已存入 Milvus！")
        else:
            logger.warning("⚠️  uuid 不存在，可能存储失败")

        return exists

    except Exception as e:
        logger.error(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_vector_search():
    """
    测试向量搜索功能
    """
    logger.info("\n" + "=" * 60)
    logger.info("测试向量搜索")
    logger.info("=" * 60 + "\n")

    from app.client.milvus_client import get_milvus_client
    from app.client.sentiment_embedding_client import SentimentEmbeddingClient

    try:
        # 1. 生成查询向量
        query_text = "人工智能大模型技术发展趋势"
        logger.info(f"🔍 查询文本: {query_text}")

        embedding_client = SentimentEmbeddingClient()
        embedding_result = await embedding_client.get_embedding(
            id="query",
            text=query_text
        )

        if not embedding_result:
            logger.error("❌ 生成查询向量失败")
            return

        query_vector = embedding_result["embedding"]
        logger.info(f"  ↳ 向量维度: {len(query_vector)}")

        # 2. 执行搜索
        client = get_milvus_client()
        client.connect()
        client.create_collection()

        results = client.search(
            query_vector=query_vector,
            top_k=5,
            threshold=0.5
        )

        logger.info(f"\n📊 搜索结果 ({len(results)} 条):")
        for i, r in enumerate(results, 1):
            logger.info(f"  {i}. uuid: {r['uuid']}, score: {r['score']:.4f}")

        if results:
            logger.success("\n✅ 向量搜索成功！")
        else:
            logger.warning("\n⚠️  未找到匹配结果（可能是阈值过高或集合为空）")

    except Exception as e:
        logger.error(f"❌ 搜索失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主测试入口"""
    logger.info("\n" + "🎯 " + "=" * 54)
    logger.info("🎯  Store to Milvus 测试套件")
    logger.info("🎯 " + "=" * 54 + "\n")

    # 1. 测试存储节点
    document_id = await test_store_to_milvus_node()

    if document_id:
        # 2. 测试查询确认
        await test_milvus_query(document_id)

        # 3. 测试向量搜索
        await test_vector_search()

    logger.info("\n" + "🎉 " + "=" * 54)
    logger.info("🎉  测试完成！")
    logger.info("🎉 " + "=" * 54 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
