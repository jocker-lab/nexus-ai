# -*- coding: utf-8 -*-
"""
@File    :   vector_service.py
@Time    :   2025/11/28
@Desc    :   向量服务 - 文档摘要提取 + 向量化 + Milvus 存储
"""

from typing import Optional
from loguru import logger
from langchain_deepseek import ChatDeepSeek

from app.agents.schemas.document_summary_schema import DocumentSummary
from app.agents.prompts.template import render_prompt_template
from app.clients.sentiment_embedding_client import SentimentEmbeddingClient
from app.clients.milvus_client import get_milvus_client

# Prompt 模板路径
PROMPT_PATH = "publisher_prompts/document_writing"


async def insert_milvus(document_id: str, content: str) -> bool:
    """
    文档向量化存储

    流程：
    1. LLM 提取 title + summary (structured output)
    2. 拼接 "{title}。{summary}" 调用 embedding 服务
    3. 存入 Milvus (document_id, embedding)

    Args:
        document_id: 文档 UUID（与 SQL Report 表的 id 一致）
        content: 文档完整内容

    Returns:
        是否成功
    """
    logger.info(f"[VectorService] 开始向量化存储: {document_id}")

    if not content:
        logger.warning("[VectorService] 文档内容为空，跳过向量化")
        return False

    # === 1. LLM 提取 title + summary ===
    logger.info("[VectorService] 步骤 1/3: 提取文档摘要...")

    try:
        llm = ChatDeepSeek(model="deepseek-chat", temperature=0)
        llm_with_structure = llm.with_structured_output(DocumentSummary)

        # 文档预览（避免 token 过多）
        doc_preview = content[:8000]
        if len(content) > 8000:
            doc_preview += f"\n\n... [省略 {len(content) - 8000} 字符] ..."

        extract_prompt = render_prompt_template(f"{PROMPT_PATH}/extract_summary", {
            "document_content": doc_preview,
        })

        summary_result: DocumentSummary = await llm_with_structure.ainvoke(extract_prompt)

        title = summary_result.title
        summary = summary_result.summary

        logger.info(f"[VectorService]   ✓ 标题: {title}")
        logger.info(f"[VectorService]   ✓ 摘要: {summary[:100]}...")

    except Exception as e:
        logger.error(f"[VectorService] 摘要提取失败: {e}")
        return False

    # === 2. 向量化 ===
    logger.info("[VectorService] 步骤 2/3: 调用 embedding 服务...")

    try:
        # 拼接 title + summary 作为向量化文本
        text_for_embedding = f"{title}。{summary}"

        # 调用 embedding 服务
        embedding_client = SentimentEmbeddingClient()
        embedding_result = await embedding_client.get_embedding(
            id=document_id,
            text=text_for_embedding
        )

        if not embedding_result or "embedding" not in embedding_result:
            logger.error("[VectorService] Embedding 服务返回空结果")
            return False

        embedding_vector = embedding_result["embedding"]
        logger.info(f"[VectorService]   ✓ 向量维度: {len(embedding_vector)}")

    except Exception as e:
        logger.error(f"[VectorService] 向量化失败: {e}")
        return False

    # === 3. 存入 Milvus ===
    logger.info("[VectorService] 步骤 3/3: 存入 Milvus...")

    try:
        milvus_client = get_milvus_client()
        success = milvus_client.insert(uuid=document_id, embedding=embedding_vector)

        if success:
            logger.success(f"[VectorService] ✓ 成功存入 Milvus: {document_id}")
            return True
        else:
            logger.error("[VectorService] Milvus 插入失败")
            return False

    except Exception as e:
        logger.error(f"[VectorService] Milvus 存储失败: {e}")
        return False


async def search_similar_documents(
    query_text: str,
    top_k: int = 5,
    threshold: Optional[float] = 0.5
) -> list:
    """
    搜索相似文档

    Args:
        query_text: 查询文本
        top_k: 返回前 k 个结果
        threshold: 相似度阈值

    Returns:
        相似文档列表 [{"uuid": "...", "score": 0.9}, ...]
    """
    logger.info(f"[VectorService] 搜索相似文档: {query_text[:50]}...")

    try:
        # 1. 查询文本向量化
        embedding_client = SentimentEmbeddingClient()
        embedding_result = await embedding_client.get_embedding(
            id="query",
            text=query_text
        )

        if not embedding_result or "embedding" not in embedding_result:
            logger.error("[VectorService] 查询向量化失败")
            return []

        query_vector = embedding_result["embedding"]

        # 2. Milvus 搜索
        milvus_client = get_milvus_client()
        results = milvus_client.search(
            query_vector=query_vector,
            top_k=top_k,
            threshold=threshold
        )

        logger.info(f"[VectorService] 找到 {len(results)} 个相似文档")
        return results

    except Exception as e:
        logger.error(f"[VectorService] 搜索失败: {e}")
        return []
