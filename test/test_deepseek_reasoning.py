#!/usr/bin/env python3
"""
测试 DeepSeek Reasoner 通过 LangChain ChatOpenAI 返回的 chunk 结构
"""
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# 从数据库获取 API key (这里用环境变量或手动配置)
import os

async def test_deepseek_reasoning():
    """测试 DeepSeek Reasoner 的流式响应结构"""

    # 配置 DeepSeek
    llm = ChatOpenAI(
        model="deepseek-reasoner",
        base_url="https://api.deepseek.com/v1",
        api_key=os.environ.get("DEEPSEEK_API_KEY", ""),  # 需要设置环境变量
        temperature=0.7,
        streaming=True,
    )

    messages = [HumanMessage(content="1+1等于多少？请解释")]

    print("=" * 60)
    print("Testing DeepSeek Reasoner streaming response structure")
    print("=" * 60)

    chunk_count = 0
    async for chunk in llm.astream(messages):
        chunk_count += 1
        print(f"\n--- Chunk {chunk_count} ---")
        print(f"Type: {type(chunk)}")
        print(f"Content: {repr(chunk.content)}")
        print(f"Additional kwargs: {chunk.additional_kwargs}")

        # 检查是否有 reasoning_content
        if hasattr(chunk, 'additional_kwargs'):
            if 'reasoning_content' in chunk.additional_kwargs:
                print(f">>> FOUND reasoning_content in additional_kwargs!")
                print(f"    Value: {chunk.additional_kwargs['reasoning_content']}")

        # 检查其他可能的属性
        for attr in dir(chunk):
            if not attr.startswith('_') and attr not in ['content', 'additional_kwargs', 'type']:
                val = getattr(chunk, attr, None)
                if val and not callable(val):
                    print(f"  {attr}: {val}")

        if chunk_count > 20:  # 限制输出
            print("\n... (truncated after 20 chunks)")
            break

if __name__ == "__main__":
    asyncio.run(test_deepseek_reasoning())
