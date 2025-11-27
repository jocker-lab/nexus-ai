"""
测试向量服务是否可用
"""
import asyncio
from app.client.sentiment_embedding_client import SentimentEmbeddingClient


async def test_embedding_service():
    print("=" * 50)
    print("测试向量服务连接")
    print("=" * 50)

    client = SentimentEmbeddingClient(
        base_url="http://127.0.0.1:8090",
        timeout=10,
        retries=1
    )

    test_text = "这是一段测试文本，用于验证向量服务是否正常运行。"
    test_id = "test_001"

    print(f"\n请求 URL: {client.endpoint}")
    print(f"测试文本: {test_text}")
    print(f"测试 ID: {test_id}")
    print("-" * 50)

    try:
        result = await client.get_embedding(test_id, test_text)

        if result:
            print(f"\n✅ 服务可用!")
            print(f"  - 返回 ID: {result.get('id')}")
            print(f"  - 向量维度: {len(result.get('embedding', []))}")
            print(f"  - 向量前5维: {result.get('embedding', [])[:5]}")
        else:
            print(f"\n❌ 服务返回空结果")

    except Exception as e:
        print(f"\n❌ 服务不可用: {type(e).__name__} - {e}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    asyncio.run(test_embedding_service())
