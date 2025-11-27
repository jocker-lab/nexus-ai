# -*- coding: utf-8 -*-
"""
Store to Milvus - 文档向量化存储节点

职责：
1. 使用 LLM 提取文档的 title 和 summary
2. 调用 embedding 服务向量化
3. 存入 Milvus 向量数据库
"""
import uuid
from typing import Dict, Any
from loguru import logger
from langchain_deepseek import ChatDeepSeek

from app.agents.core.publisher.writing.state import DocumentState
from app.agents.schemas.document_summary_schema import DocumentSummary
from app.agents.prompts.template import render_prompt_template
from app.client.sentiment_embedding_client import SentimentEmbeddingClient
from app.client.milvus_client import get_milvus_client

# Prompt 模板路径
PROMPT_PATH = "publisher_prompts/document_writing"


async def store_to_milvus(state: DocumentState) -> Dict[str, Any]:
    """
    文档向量化存储节点

    流程：
    1. 从 final_document 提取 title + summary (LLM structured output)
    2. 拼接 "{title}。{summary}" 调用 embedding 服务
    3. 生成 UUID，存入 Milvus (uuid, embedding)
    4. 返回 document_id 供后续使用

    注意：其他元数据（date, domain, full_content）存入 SQL，不在此处理
    """
    logger.info("\n💾 [Store to Milvus] 开始文档向量化存储...")

    final_document = state.get("final_document", "")
    if not final_document:
        logger.warning("  ⚠️  final_document 为空，跳过向量化存储")
        return {"document_id": ""}

    # === 1. 提取 title + summary ===
    logger.info("  ↳ 步骤 1/3: 提取文档摘要...")

    try:
        llm = ChatDeepSeek(model="deepseek-chat", temperature=0)
        llm_with_structure = llm.with_structured_output(DocumentSummary)

        # 文档预览（避免 token 过多）
        doc_preview = final_document[:8000]
        if len(final_document) > 8000:
            doc_preview += f"\n\n... [省略 {len(final_document) - 8000} 字符] ..."

        extract_prompt = render_prompt_template(f"{PROMPT_PATH}/extract_summary", {
            "document_content": doc_preview,
        })

        summary_result: DocumentSummary = await llm_with_structure.ainvoke(extract_prompt)

        title = summary_result.title
        summary = summary_result.summary

        logger.info(f"    ✓ 标题: {title}")
        logger.info(f"    ✓ 摘要: {summary[:100]}...")

    except Exception as e:
        logger.error(f"  ❌ 摘要提取失败: {e}")
        return {"document_id": ""}

    # === 2. 向量化 ===
    logger.info("  ↳ 步骤 2/3: 调用 embedding 服务...")

    try:
        # 拼接 title + summary 作为向量化文本
        text_for_embedding = f"{title}。{summary}"

        # 生成 UUID
        doc_uuid = str(uuid.uuid4())

        # 调用 embedding 服务
        embedding_client = SentimentEmbeddingClient()
        embedding_result = await embedding_client.get_embedding(
            id=doc_uuid,
            text=text_for_embedding
        )

        if not embedding_result or "embedding" not in embedding_result:
            logger.error("  ❌ Embedding 服务返回空结果")
            return {"document_id": ""}

        embedding_vector = embedding_result["embedding"]
        logger.info(f"    ✓ 向量维度: {len(embedding_vector)}")

    except Exception as e:
        logger.error(f"  ❌ 向量化失败: {e}")
        return {"document_id": ""}

    # === 3. 存入 Milvus ===
    logger.info("  ↳ 步骤 3/3: 存入 Milvus...")

    try:
        milvus_client = get_milvus_client()
        success = milvus_client.insert(uuid=doc_uuid, embedding=embedding_vector)

        if success:
            logger.success(f"  ✓ 成功存入 Milvus: {doc_uuid}")
        else:
            logger.error("  ❌ Milvus 插入失败")
            return {"document_id": ""}

    except Exception as e:
        logger.error(f"  ❌ Milvus 存储失败: {e}")
        return {"document_id": ""}

    logger.success(f"\n✅ [Store to Milvus] 完成！document_id: {doc_uuid}\n")

    return {
        "document_id": doc_uuid,
    }
