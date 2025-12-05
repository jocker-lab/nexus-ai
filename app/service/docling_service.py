# -*- coding: utf-8 -*-
"""
@File    :   docling_service.py
@Desc    :   Docling 文件解析服务 - 将各种文档格式转换为 Markdown
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict, Any

from loguru import logger
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter

# 全局单例
_converter_instance = None

# 全局线程池
_thread_pool = ThreadPoolExecutor(max_workers=5)


def get_converter() -> DocumentConverter:
    """获取 DocumentConverter 单例"""
    global _converter_instance
    if _converter_instance is None:
        logger.info("[DoclingService] 初始化 DocumentConverter...")
        _converter_instance = DocumentConverter(
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.DOCX,
                InputFormat.HTML,
                InputFormat.MD,
                InputFormat.XLSX,
                InputFormat.PPTX,
            ]
        )
        logger.info("[DoclingService] DocumentConverter 初始化完成")
    return _converter_instance


async def parse_document(
    url: str,
    timeout: int = 60,
) -> Optional[str]:
    """
    解析单个文档 URL 为 Markdown

    Args:
        url: 文档 URL（可以是网页 URL 或 MinIO URL）
        timeout: 超时时间（秒）

    Returns:
        Markdown 字符串，失败返回 None
    """
    logger.info(f"[DoclingService] 解析文档: {url}")

    converter = get_converter()

    try:
        loop = asyncio.get_running_loop()

        # 在线程池中执行 converter.convert
        result = await asyncio.wait_for(
            loop.run_in_executor(
                _thread_pool,
                converter.convert,
                url
            ),
            timeout=timeout
        )

        markdown_content = result.document.export_to_markdown()
        logger.info(f"[DoclingService] 解析成功，内容长度: {len(markdown_content)} 字符")
        return markdown_content

    except asyncio.TimeoutError:
        logger.error(f"[DoclingService] 解析超时 ({timeout}秒): {url}")
        return None
    except Exception as e:
        logger.error(f"[DoclingService] 解析失败: {e}")
        return None


async def parse_documents(
    documents: List[Dict[str, str]],
    timeout_per_doc: int = 60,
) -> List[Dict[str, Any]]:
    """
    批量解析多个文档

    Args:
        documents: 文档列表，每项包含 {"label": "...", "url": "..."}
        timeout_per_doc: 每个文档的超时时间（秒）

    Returns:
        解析结果列表，每项包含 {"label": "...", "url": "...", "content": "..."}
    """
    if not documents:
        return []

    logger.info(f"[DoclingService] 批量解析 {len(documents)} 个文档")

    async def parse_single(doc: Dict[str, str]) -> Dict[str, Any]:
        url = doc["url"]
        label = doc.get("label", "")

        content = await parse_document(url, timeout=timeout_per_doc)

        return {
            "label": label,
            "url": url,
            "content": content if content else "解析失败"
        }

    tasks = [parse_single(doc) for doc in documents]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 过滤异常结果
    return [r for r in results if isinstance(r, dict)]
