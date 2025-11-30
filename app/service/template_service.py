# -*- coding: utf-8 -*-
"""
@File    :   template_service.py
@Time    :   2025/11/28
@Desc    :   模版服务 - 文件解析 + 大纲提取 + 向量化存储
"""

import uuid
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
from loguru import logger
from langchain.chat_models import init_chat_model

from app.schemas.template_outline_schema import TemplateOutline
from app.agents.prompts.template import render_prompt_template
from app.clients.sentiment_embedding_client import SentimentEmbeddingClient
from app.clients.milvus_client import MilvusClient
from app.curd.templates import Templates

load_dotenv()

# Prompt 模板路径
PROMPT_PATH = "template_prompts"

# 模版向量集合名称（与文档向量分开）
TEMPLATE_COLLECTION = "template_vectors"


def get_template_milvus_client() -> MilvusClient:
    """获取模版专用的 Milvus 客户端"""
    return MilvusClient(collection_name=TEMPLATE_COLLECTION)


async def upload_template(
    file_content: str,
    original_filename: str,
    user_id: str,
) -> Optional[Dict[str, Any]]:
    """
    上传模版处理

    流程：
    1. 接收文件内容（已经由 Docling 转换为 Markdown）
    2. LLM + structured_output 提取模版大纲
    3. Embedding 向量化
    4. 存储：SQL + Milvus

    Args:
        file_content: Markdown 格式的文件内容（Docling 转换后）
        original_filename: 原始文件名
        user_id: 用户ID

    Returns:
        {"template_id": "xxx", "title": "...", "outline": {...}} 或 None
    """
    logger.info(f"[TemplateService] 开始处理模版上传: {original_filename}")

    if not file_content:
        logger.warning("[TemplateService] 文件内容为空")
        return None

    # === 1. LLM 提取模版大纲 ===
    logger.info("[TemplateService] 步骤 1/3: 提取模版大纲...")

    try:
        llm = init_chat_model("deepseek:deepseek-chat", temperature=0)
        llm_with_structure = llm.with_structured_output(TemplateOutline)

        # 文档预览（避免 token 过多）
        doc_preview = file_content[:10000]
        if len(file_content) > 10000:
            doc_preview += f"\n\n... [省略 {len(file_content) - 10000} 字符] ..."

        extract_prompt = render_prompt_template(f"{PROMPT_PATH}/extract_template_outline", {
            "document_content": doc_preview,
        })

        outline_result: TemplateOutline = await llm_with_structure.ainvoke(extract_prompt)

        logger.info(f"[TemplateService]   ✓ 标题: {outline_result.title}")
        logger.info(f"[TemplateService]   ✓ 分类: {outline_result.category}")
        logger.info(f"[TemplateService]   ✓ 章节数: {len(outline_result.sections)}")

    except Exception as e:
        logger.error(f"[TemplateService] 大纲提取失败: {e}")
        return None

    # === 2. 向量化 ===
    logger.info("[TemplateService] 步骤 2/3: 向量化...")

    try:
        # 生成模版ID
        template_id = str(uuid.uuid4())

        # 拼接用于向量化的文本
        text_for_embedding = f"{outline_result.title}。{outline_result.summary}"

        embedding_client = SentimentEmbeddingClient()
        embedding_result = await embedding_client.get_embedding(
            id=template_id,
            text=text_for_embedding
        )

        if not embedding_result or "embedding" not in embedding_result:
            logger.error("[TemplateService] Embedding 服务返回空结果")
            return None

        embedding_vector = embedding_result["embedding"]
        logger.info(f"[TemplateService]   ✓ 向量维度: {len(embedding_vector)}")

    except Exception as e:
        logger.error(f"[TemplateService] 向量化失败: {e}")
        return None

    # === 3. 存储 ===
    logger.info("[TemplateService] 步骤 3/3: 存储...")

    try:
        # 3.1 存入 Milvus
        milvus_client = get_template_milvus_client()
        milvus_success = milvus_client.insert(uuid=template_id, embedding=embedding_vector)

        if not milvus_success:
            logger.error("[TemplateService] Milvus 插入失败")
            return None

        logger.info(f"[TemplateService]   ✓ Milvus 存储成功")

        # 3.2 存入 SQL
        # 将 sections 转换为可序列化的格式
        sections_data = [
            {
                "title": s.title,
                "description": s.description,
                "estimated_percentage": s.estimated_percentage,
                "key_points": s.key_points,
            }
            for s in outline_result.sections
        ]

        template = Templates.create_template(
            template_id=template_id,
            user_id=user_id,
            title=outline_result.title,
            summary=outline_result.summary,
            category=outline_result.category,
            original_filename=original_filename,
            markdown_content=file_content,
            writing_style=outline_result.writing_style,
            writing_tone=outline_result.writing_tone,
            target_audience=outline_result.target_audience,
            sections=sections_data,
            special_requirements=outline_result.special_requirements,
        )

        if not template:
            logger.error("[TemplateService] SQL 插入失败")
            # TODO: 回滚 Milvus
            return None

        logger.info(f"[TemplateService]   ✓ SQL 存储成功")

    except Exception as e:
        logger.error(f"[TemplateService] 存储失败: {e}")
        return None

    logger.success(f"[TemplateService] ✓ 模版上传完成: {template_id}")

    return {
        "template_id": template_id,
        "title": outline_result.title,
        "category": outline_result.category,
        "summary": outline_result.summary,
        "sections_count": len(outline_result.sections),
    }


async def search_templates(
    query_text: str,
    top_k: int = 5,
    threshold: Optional[float] = 0.5,
) -> List[Dict[str, Any]]:
    """
    搜索相似模版（给 Planner Tool 用）

    Args:
        query_text: 查询文本（如用户的写作需求）
        top_k: 返回前 k 个结果
        threshold: 相似度阈值

    Returns:
        模版列表，每项包含完整模版信息
    """
    logger.info(f"[TemplateService] 搜索模版: {query_text[:50]}...")

    try:
        # 1. 查询文本向量化
        embedding_client = SentimentEmbeddingClient()
        embedding_result = await embedding_client.get_embedding(
            id="query",
            text=query_text
        )

        if not embedding_result or "embedding" not in embedding_result:
            logger.error("[TemplateService] 查询向量化失败")
            return []

        query_vector = embedding_result["embedding"]

        # 2. Milvus 搜索
        milvus_client = get_template_milvus_client()
        search_results = milvus_client.search(
            query_vector=query_vector,
            top_k=top_k,
            threshold=threshold
        )

        if not search_results:
            logger.info("[TemplateService] 未找到匹配模版")
            return []

        # 3. 根据 uuid 查询 SQL 获取完整信息
        template_ids = [r["uuid"] for r in search_results]
        templates = Templates.get_templates_by_ids(template_ids)

        # 构建返回结果（包含相似度分数）
        score_map = {r["uuid"]: r["score"] for r in search_results}
        results = []
        for t in templates:
            results.append({
                "template_id": t.id,
                "title": t.title,
                "summary": t.summary,
                "category": t.category,
                "writing_style": t.writing_style,
                "writing_tone": t.writing_tone,
                "target_audience": t.target_audience,
                "sections": t.sections,  # 每个章节包含 estimated_percentage
                "special_requirements": t.special_requirements,
                "similarity_score": score_map.get(t.id, 0),
            })

        # 按相似度排序
        results.sort(key=lambda x: x["similarity_score"], reverse=True)

        logger.info(f"[TemplateService] 找到 {len(results)} 个匹配模版")
        return results

    except Exception as e:
        logger.error(f"[TemplateService] 搜索失败: {e}")
        return []


async def delete_template(template_id: str, user_id: str) -> bool:
    """
    删除模版（同时删除 SQL 和 Milvus）

    Args:
        template_id: 模版ID
        user_id: 用户ID

    Returns:
        是否成功
    """
    logger.info(f"[TemplateService] 删除模版: {template_id}")

    try:
        # 1. 删除 Milvus
        milvus_client = get_template_milvus_client()
        milvus_client.delete(uuid=template_id)

        # 2. 删除 SQL
        sql_success = Templates.delete_template(template_id, user_id)

        if sql_success:
            logger.success(f"[TemplateService] ✓ 模版删除成功: {template_id}")
            return True
        else:
            logger.warning(f"[TemplateService] SQL 删除失败或无权限")
            return False

    except Exception as e:
        logger.error(f"[TemplateService] 删除失败: {e}")
        return False
