# -*- coding: utf-8 -*-
"""
@File    :   documents.py
@Time    :   2025/12/03
@Author  :   pygao
@Version :   2.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文档API端点（从 reports.py 重命名）
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional

from app.schemas.documents import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListItem,
    DocumentVersionResponse,
    DocumentVersionDetail,
    VersionRollbackRequest,
    DocumentSessionCreate,
    DocumentSessionResponse,
    OutlineUpdateRequest
)
from app.curd.documents import Documents, DocumentVersions
from app.models.documents import DocumentStatus

router = APIRouter()


# ==================== 文档基础操作 ====================

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    user_id: str = "user-123"  # 实际应从认证中间件获取
):
    """
    创建新文档

    支持：
    - 直接创建空白文档
    - 关联会话ID（用于交互式生成）
    - 初始化章节大纲
    """
    document = Documents.create_document(
        user_id=user_id,
        title=document_data.title,
        content=document_data.content,
        description=document_data.description,
        chat_id=document_data.chat_id,
        outline=document_data.outline,
        category=document_data.category,
        tags=document_data.tags,
        status=DocumentStatus(document_data.status) if document_data.status else DocumentStatus.DRAFT
    )

    if not document:
        raise HTTPException(status_code=500, detail="Failed to create document")

    return document


@router.get("/public/{document_id}", response_model=DocumentResponse)
async def get_public_document(document_id: str):
    """
    公开访问文档（无需认证）
    """
    document = Documents.get_document_by_id(document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    user_id: str = "user-123"
):
    """获取文档详情（包含完整内容和大纲）"""
    document = Documents.get_document_by_id_and_user_id(document_id, user_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.get("", response_model=List[DocumentListItem])
async def list_documents(
    user_id: str = "user-123",
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    获取用户的文档列表

    支持筛选：
    - status: draft/published/archived
    - 分页：limit, offset
    """
    document_status = DocumentStatus(status) if status else None
    documents = Documents.get_documents_by_user_id(
        user_id=user_id,
        status=document_status,
        limit=limit,
        offset=offset
    )

    return documents


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    user_id: str = "user-123"
):
    """
    更新文档

    特性：
    - 自动创建版本快照
    - 用户编辑会标记is_manually_edited=True
    - 支持change_summary记录变更说明
    """
    document = Documents.update_document(
        document_id=document_id,
        user_id=user_id,
        title=document_update.title,
        content=document_update.content,
        description=document_update.description,
        outline=document_update.outline,
        status=DocumentStatus(document_update.status) if document_update.status else None,
        category=document_update.category,
        tags=document_update.tags,
        change_summary=document_update.change_summary,
        changed_by="user"
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found or update failed")

    return document


@router.post("/{document_id}/publish", response_model=DocumentResponse)
async def publish_document(
    document_id: str,
    user_id: str = "user-123"
):
    """
    发布文档

    操作：
    - 状态变更为PUBLISHED
    - 记录published_at时间戳
    - 创建发布版本快照
    """
    document = Documents.publish_document(document_id, user_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    user_id: str = "user-123"
):
    """
    删除文档

    注意：会同时删除所有版本历史
    """
    success = Documents.delete_document(document_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Document not found")


# ==================== 版本管理操作 ====================

@router.get("/{document_id}/versions", response_model=List[DocumentVersionResponse])
async def get_document_versions(
    document_id: str,
    user_id: str = "user-123",
    limit: int = 50
):
    """
    获取文档的版本历史列表

    返回：
    - 版本号、变更类型、变更人、时间等元数据
    - 不包含完整content（节省带宽）
    """
    # 验证权限
    document = Documents.get_document_by_id_and_user_id(document_id, user_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    versions = DocumentVersions.get_versions_by_document_id(document_id, limit)
    return versions


@router.get("/{document_id}/versions/{version_number}", response_model=DocumentVersionDetail)
async def get_version_detail(
    document_id: str,
    version_number: int,
    user_id: str = "user-123"
):
    """
    获取指定版本的完整内容

    用于：
    - 版本对比
    - 查看历史内容
    """
    # 验证权限
    document = Documents.get_document_by_id_and_user_id(document_id, user_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    version = DocumentVersions.get_version_by_number(document_id, version_number)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    return version


@router.post("/{document_id}/rollback", response_model=DocumentResponse)
async def rollback_to_version(
    document_id: str,
    rollback_request: VersionRollbackRequest,
    user_id: str = "user-123"
):
    """
    回滚到指定版本

    实现方式：
    - 从历史版本复制内容
    - 创建新版本（不是真删除）
    - 保留完整历史记录
    """
    document = DocumentVersions.rollback_to_version(
        document_id=document_id,
        user_id=user_id,
        version_number=rollback_request.version_number
    )

    if not document:
        raise HTTPException(status_code=404, detail="Rollback failed")

    return document


# ==================== 交互式文档生成 ====================

@router.post("/sessions", response_model=DocumentSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_document_session(
    session_data: DocumentSessionCreate,
    user_id: str = "user-123"
):
    """
    创建文档生成会话

    流程：
    1. 创建Chat记录（meta.type="document_generation"）
    2. 创建空白Document（关联chat_id）
    3. 启动Blueprint Agent生成大纲
    4. 返回chat_id和thread_id供后续交互

    注：此接口需要集成LangGraph Blueprint Agent
    """
    import uuid
    import time
    from app.models.chats import Chat
    from app.database.db import get_db_context

    # 1. 创建会话
    chat_id = str(uuid.uuid4())
    thread_id = f"blueprint-{chat_id}"

    chat_meta = {
        "type": "document_generation",
        "document_metadata": {
            "topic": session_data.topic,
            "research_depth": session_data.research_depth,
            "target_audience": session_data.target_audience,
            "blueprint_config": {
                "recursion_limit": 50,
                "thread_id": thread_id
            }
        },
        "tags": session_data.tags.split(",") if session_data.tags else []
    }

    with get_db_context() as db:
        chat = Chat(
            id=chat_id,
            user_id=user_id,
            title=f"文档生成：{session_data.topic}",
            chat={},
            meta=chat_meta,
            created_at=int(time.time()),
            updated_at=int(time.time())
        )
        db.add(chat)
        db.commit()

    # 2. 创建文档
    document = Documents.create_document(
        user_id=user_id,
        title=session_data.topic,
        content="",
        chat_id=chat_id,
        category=session_data.category,
        tags=session_data.tags,
        outline={
            "total_chapters": 0,
            "current_chapter": 0,
            "chapters": [],
            "generation_meta": {
                "blueprint_thread_id": thread_id,
                "generation_started_at": int(time.time())
            }
        }
    )

    if not document:
        raise HTTPException(status_code=500, detail="Failed to create document session")

    # TODO: 启动Blueprint Agent
    # await start_blueprint_agent(thread_id, session_data.topic, ...)

    return DocumentSessionResponse(
        chat_id=chat_id,
        document_id=document.id,
        blueprint_thread_id=thread_id,
        topic=session_data.topic
    )


@router.patch("/{document_id}/outline", response_model=DocumentResponse)
async def update_document_outline(
    document_id: str,
    outline_update: OutlineUpdateRequest,
    user_id: str = "user-123"
):
    """
    更新文档大纲

    用途：
    - Blueprint Agent生成大纲后更新
    - 用户手动调整章节结构
    - 写作过程中更新章节状态

    注：此操作不创建版本（仅更新outline字段）
    """
    document = Documents.get_document_by_id_and_user_id(document_id, user_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    updated_document = Documents.update_outline(document_id, outline_update.outline)

    if not updated_document:
        raise HTTPException(status_code=500, detail="Failed to update outline")

    return updated_document


# ==================== 会话相关操作 ====================

@router.get("/by-chat/{chat_id}", response_model=DocumentResponse)
async def get_document_by_chat_id(
    chat_id: str,
    user_id: str = "user-123"
):
    """根据会话ID获取关联的文档"""
    document = Documents.get_document_by_chat_id(chat_id)

    if not document:
        raise HTTPException(status_code=404, detail="No document found for this chat")

    # 验证权限
    if document.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return document
