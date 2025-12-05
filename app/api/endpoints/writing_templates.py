# -*- coding: utf-8 -*-
"""
@File    :   writing_templates.py
@Time    :   2025/12/03
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   写作模版 API 端点
"""
import uuid
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Query
from typing import Optional
from loguru import logger

from app.schemas.writing_templates import (
    WritingTemplateCreate,
    WritingTemplateUpdate,
    WritingTemplateResponse,
    WritingTemplateListItem,
    WritingTemplateListResponse,
    UseTemplateResponse
)
from app.curd.writing_templates import WritingTemplates
from app.models.writing_templates import (
    WritingStyle,
    WritingTone,
    TemplateStatus,
    TemplateScope
)
from app.database.minio_db import get_minio_client
from app.tasks.template_tasks import process_template_file

router = APIRouter()

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.md', '.txt'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


# ==================== 文件上传与解析进度 ====================

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_template_file(
    file: UploadFile = File(...),
    user_id: str = Query(default="user-123", description="用户ID")
):
    """
    上传模版文件，触发 Celery 异步解析

    流程：
    1. 验证文件类型和大小
    2. 上传到 MinIO pending bucket
    3. 创建 WritingTemplate 记录（status=pending）
    4. 触发 Celery 任务 process_template_file
    5. 返回 template_id 和 task_id

    支持的文件类型：.pdf, .docx, .doc, .md, .txt
    最大文件大小：50MB
    """
    # 1. 验证文件扩展名
    filename = file.filename or "unknown"
    file_ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file_ext}。支持的类型: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 2. 读取文件内容
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件过大: {file_size / 1024 / 1024:.2f}MB，最大允许: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件内容为空"
        )

    # 3. 生成唯一标识
    template_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    object_name = f"{user_id}/{template_id}/{filename}"

    # 4. 上传到 MinIO pending bucket
    try:
        minio_client = get_minio_client()
        file_url = minio_client.upload_pending_file(
            file_data=file_content,
            object_name=object_name,
            content_type=file.content_type or "application/octet-stream"
        )
        logger.info(f"[UploadTemplate] 文件上传到 MinIO: {file_url}")
    except Exception as e:
        logger.error(f"[UploadTemplate] MinIO 上传失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件上传失败"
        )

    # 5. 创建 WritingTemplate 记录（status=pending）
    template = WritingTemplates.create_template(
        user_id=user_id,
        title=filename,  # 初始标题使用文件名，后续 LLM 解析后会更新
        summary="正在解析中...",
        original_filename=filename,
        status=TemplateStatus.PENDING
    )

    if not template:
        # 清理已上传的文件
        minio_client.delete_pending_file(object_name)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建模版记录失败"
        )

    # 6. 触发 Celery 任务
    try:
        celery_task = process_template_file.delay(
            task_id=task_id,
            file_url=file_url,
            object_name=object_name,
            filename=filename,
            user_id=user_id,
        )
        logger.info(f"[UploadTemplate] Celery 任务已提交: {celery_task.id}")
    except Exception as e:
        logger.error(f"[UploadTemplate] Celery 任务提交失败: {e}")
        # 任务提交失败时更新状态
        WritingTemplates.update_template_status(
            template_id=template.id,
            status=TemplateStatus.FAILED,
            error_message="任务提交失败"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="任务提交失败"
        )

    return {
        "template_id": template.id,
        "task_id": celery_task.id,
        "filename": filename,
        "status": "pending",
        "message": "文件已上传，正在解析中..."
    }


@router.get("/{template_id}/progress")
async def get_parse_progress(
    template_id: str,
    user_id: str = Query(default="user-123", description="用户ID")
):
    """
    获取模版解析进度

    返回：
    - status: pending/parsing/completed/failed
    - progress: 进度百分比（0-100）
    - current_step: 当前步骤描述
    - error_message: 错误信息（如果失败）
    """
    # 获取模版记录
    template = WritingTemplates.get_template_by_id_and_user_id(template_id, user_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模版不存在或无权访问"
        )

    # 根据状态计算进度
    status_progress_map = {
        TemplateStatus.PENDING: (0, "等待处理"),
        TemplateStatus.PARSING: (50, "正在解析文档"),
        TemplateStatus.COMPLETED: (100, "解析完成"),
        TemplateStatus.FAILED: (0, "解析失败"),
    }

    progress, current_step = status_progress_map.get(
        template.status,
        (0, "未知状态")
    )

    return {
        "template_id": template_id,
        "status": template.status.value if hasattr(template.status, 'value') else str(template.status),
        "progress": progress,
        "current_step": current_step,
        "error_message": template.error_message,
        "title": template.title if template.status == TemplateStatus.COMPLETED else None,
        "category": template.category if template.status == TemplateStatus.COMPLETED else None,
    }


# ==================== 模版基础操作 ====================

@router.post("", response_model=WritingTemplateResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=WritingTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: WritingTemplateCreate,
    user_id: str = "user-123"  # 实际应从认证中间件获取
):
    """
    创建新写作模版

    支持：
    - 手动创建模版
    - 从文档解析创建（设置 original_filename）
    """
    template = WritingTemplates.create_template(
        user_id=user_id,
        title=template_data.title,
        summary=template_data.summary,
        category=template_data.category,
        original_filename=template_data.original_filename,
        markdown_content=template_data.markdown_content,
        writing_style=WritingStyle(template_data.writing_style.value) if template_data.writing_style else WritingStyle.BUSINESS,
        writing_tone=WritingTone(template_data.writing_tone.value) if template_data.writing_tone else WritingTone.NEUTRAL,
        target_audience=template_data.target_audience,
        sections=template_data.sections,
        scope=TemplateScope(template_data.scope.value) if template_data.scope else TemplateScope.PRIVATE
    )

    if not template:
        raise HTTPException(status_code=500, detail="Failed to create template")

    return template


@router.get("/{template_id}", response_model=WritingTemplateResponse)
async def get_template(
    template_id: str,
    user_id: str = "user-123"
):
    """
    获取模版详情

    权限：
    - 可以访问自己的模版
    - 可以访问公开模版
    """
    template = WritingTemplates.get_accessible_template(template_id, user_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.get("", response_model=WritingTemplateListResponse)
@router.get("/", response_model=WritingTemplateListResponse)
async def list_templates(
    user_id: str = "user-123",
    status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    获取用户的模版列表

    支持筛选：
    - status: pending/parsing/completed/failed
    - category: 分类筛选
    - 分页：page, page_size
    """
    template_status = TemplateStatus(status) if status else None
    offset = (page - 1) * page_size

    templates, total = WritingTemplates.get_templates_by_user_id(
        user_id=user_id,
        status=template_status,
        category=category,
        limit=page_size,
        offset=offset
    )

    return WritingTemplateListResponse(
        items=[WritingTemplateListItem.model_validate(t) for t in templates],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/public/list", response_model=WritingTemplateListResponse)
async def list_public_templates(
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    获取公开模版列表

    特性：
    - 只返回已完成解析的公开模版
    - 按使用次数排序
    """
    offset = (page - 1) * page_size

    templates, total = WritingTemplates.get_public_templates(
        category=category,
        limit=page_size,
        offset=offset
    )

    return WritingTemplateListResponse(
        items=[WritingTemplateListItem.model_validate(t) for t in templates],
        total=total,
        page=page,
        page_size=page_size
    )


@router.patch("/{template_id}", response_model=WritingTemplateResponse)
async def update_template(
    template_id: str,
    template_update: WritingTemplateUpdate,
    user_id: str = "user-123"
):
    """
    更新模版

    注意：只能更新自己的模版
    """
    template = WritingTemplates.update_template(
        template_id=template_id,
        user_id=user_id,
        title=template_update.title,
        summary=template_update.summary,
        category=template_update.category,
        markdown_content=template_update.markdown_content,
        writing_style=WritingStyle(template_update.writing_style.value) if template_update.writing_style else None,
        writing_tone=WritingTone(template_update.writing_tone.value) if template_update.writing_tone else None,
        target_audience=template_update.target_audience,
        sections=template_update.sections,
        status=TemplateStatus(template_update.status.value) if template_update.status else None,
        error_message=template_update.error_message,
        scope=TemplateScope(template_update.scope.value) if template_update.scope else None
    )

    if not template:
        raise HTTPException(status_code=404, detail="Template not found or update failed")

    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: str,
    user_id: str = "user-123"
):
    """
    删除模版

    注意：只能删除自己的模版
    """
    success = WritingTemplates.delete_template(template_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Template not found")


# ==================== 使用模版 ====================

@router.post("/{template_id}/use", response_model=UseTemplateResponse)
async def use_template(
    template_id: str,
    user_id: str = "user-123"
):
    """
    使用模版

    操作：
    - 增加使用次数统计
    - 可在此基础上扩展：创建关联文档等

    权限：
    - 可以使用自己的模版
    - 可以使用公开模版
    """
    # 检查权限
    template = WritingTemplates.get_accessible_template(template_id, user_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # 增加使用次数
    updated_template = WritingTemplates.increment_usage_count(template_id)

    if not updated_template:
        raise HTTPException(status_code=500, detail="Failed to use template")

    return UseTemplateResponse(
        template_id=template_id,
        usage_count=updated_template.usage_count,
        message="模版使用成功"
    )
