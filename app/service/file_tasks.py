# -*- coding: utf-8 -*-
"""
@File    :   file_tasks.py
@Desc    :   Celery 文件处理任务
"""

import asyncio
from loguru import logger

from app.celery_app import celery_app
from app.service.docling_service import parse_document
from app.service.template_service import upload_template
from app.database.minio_db import get_minio_client


def run_async(coro):
    """在同步环境中运行异步函数"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery_app.task(bind=True, name="process_template_file")
def process_template_file(
    self,
    task_id: str,
    file_url: str,
    object_name: str,
    filename: str,
    user_id: str,
):
    """
    处理上传的模版文件

    流程：
    1. 从 MinIO URL 用 Docling 解析为 Markdown
    2. 调用 upload_template() 处理（LLM提取 + 向量化 + 存储）
    3. 删除 pending bucket 中的原文件

    Args:
        task_id: 任务ID
        file_url: MinIO 文件的公开 URL
        object_name: MinIO 中的对象路径（用于删除）
        filename: 原始文件名
        user_id: 用户ID
    """
    logger.info(f"[FileTask] 开始处理文件: {filename}, task_id: {task_id}")

    try:
        # 更新任务状态
        self.update_state(state="PROCESSING", meta={"step": "docling_parsing"})

        # 1. Docling 解析为 Markdown
        logger.info(f"[FileTask] 步骤 1/3: Docling 解析...")
        markdown_content = run_async(parse_document(file_url, timeout=120))

        if not markdown_content:
            logger.error(f"[FileTask] Docling 解析失败: {filename}")
            return {
                "success": False,
                "task_id": task_id,
                "error": "文件解析失败"
            }

        logger.info(f"[FileTask] Docling 解析成功，内容长度: {len(markdown_content)} 字符")

        # 2. 调用 template_service 处理
        self.update_state(state="PROCESSING", meta={"step": "template_extraction"})
        logger.info(f"[FileTask] 步骤 2/3: 模版提取...")

        result = run_async(upload_template(
            file_content=markdown_content,
            original_filename=filename,
            user_id=user_id,
        ))

        if not result:
            logger.error(f"[FileTask] 模版提取失败: {filename}")
            return {
                "success": False,
                "task_id": task_id,
                "error": "模版提取失败"
            }

        # 检查是否为重复文档
        if result.get("error") == "duplicate":
            logger.warning(f"[FileTask] 检测到重复文档: {filename}")
            # 清理临时文件
            minio_client = get_minio_client()
            minio_client.delete_pending_file(object_name)
            return {
                "success": False,
                "task_id": task_id,
                "error": "duplicate",
                "message": result.get("message"),
                "duplicate_template_id": result.get("duplicate_template_id"),
                "duplicate_title": result.get("duplicate_title"),
                "similarity": result.get("similarity"),
            }

        logger.info(f"[FileTask] 模版提取成功: {result.get('template_id')}")

        # 3. 删除 pending bucket 中的文件
        self.update_state(state="PROCESSING", meta={"step": "cleanup"})
        logger.info(f"[FileTask] 步骤 3/3: 清理临时文件...")

        minio_client = get_minio_client()
        minio_client.delete_pending_file(object_name)

        logger.success(f"[FileTask] 文件处理完成: {filename}, template_id: {result.get('template_id')}")

        return {
            "success": True,
            "task_id": task_id,
            "template_id": result.get("template_id"),
            "title": result.get("title"),
            "category": result.get("category"),
        }

    except Exception as e:
        logger.error(f"[FileTask] 处理失败: {e}")
        return {
            "success": False,
            "task_id": task_id,
            "error": str(e)
        }
