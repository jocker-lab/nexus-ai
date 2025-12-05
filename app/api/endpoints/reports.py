# -*- coding: utf-8 -*-
"""
@File    :   reports.py
@Time    :   2025/10/10 10:06
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional

from app.schemas.reports import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportListItem,
    ReportVersionResponse,
    ReportVersionDetail,
    VersionRollbackRequest,
    ReportSessionCreate,
    ReportSessionResponse,
    OutlineUpdateRequest
)
from app.curd.reports import Reports, ReportVersions
from app.models.reports import ReportStatus

router = APIRouter()


# ==================== 报告基础操作 ====================

@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    user_id: str = "user-123"  # 实际应从认证中间件获取
):
    """
    创建新报告

    支持：
    - 直接创建空白报告
    - 关联会话ID（用于交互式生成）
    - 初始化章节大纲
    """
    report = Reports.create_report(
        user_id=user_id,
        title=report_data.title,
        content=report_data.content,
        description=report_data.description,
        chat_id=report_data.chat_id,
        outline=report_data.outline,
        category=report_data.category,
        tags=report_data.tags,
        status=ReportStatus(report_data.status) if report_data.status else ReportStatus.DRAFT
    )

    if not report:
        raise HTTPException(status_code=500, detail="Failed to create report")

    return report


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    user_id: str = "user-123"
):
    """获取报告详情（包含完整内容和大纲）"""
    report = Reports.get_report_by_id_and_user_id(report_id, user_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@router.get("", response_model=List[ReportListItem])
@router.get("/", response_model=List[ReportListItem])
async def list_reports(
    user_id: str = "user-123",
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    获取用户的报告列表

    支持筛选：
    - status: draft/published/archived
    - 分页：limit, offset
    """
    report_status = ReportStatus(status) if status else None
    reports = Reports.get_reports_by_user_id(
        user_id=user_id,
        status=report_status,
        limit=limit,
        offset=offset
    )

    return reports


@router.patch("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: str,
    report_update: ReportUpdate,
    user_id: str = "user-123"
):
    """
    更新报告

    特性：
    - 自动创建版本快照
    - 用户编辑会标记is_manually_edited=True
    - 支持change_summary记录变更说明
    """
    report = Reports.update_report(
        report_id=report_id,
        user_id=user_id,
        title=report_update.title,
        content=report_update.content,
        description=report_update.description,
        outline=report_update.outline,
        status=ReportStatus(report_update.status) if report_update.status else None,
        category=report_update.category,
        tags=report_update.tags,
        change_summary=report_update.change_summary,
        changed_by="user"
    )

    if not report:
        raise HTTPException(status_code=404, detail="Report not found or update failed")

    return report


@router.post("/{report_id}/publish", response_model=ReportResponse)
async def publish_report(
    report_id: str,
    user_id: str = "user-123"
):
    """
    发布报告

    操作：
    - 状态变更为PUBLISHED
    - 记录published_at时间戳
    - 创建发布版本快照
    """
    report = Reports.publish_report(report_id, user_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str,
    user_id: str = "user-123"
):
    """
    删除报告

    注意：会同时删除所有版本历史
    """
    success = Reports.delete_report(report_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Report not found")


# ==================== 版本管理操作 ====================

@router.get("/{report_id}/versions", response_model=List[ReportVersionResponse])
async def get_report_versions(
    report_id: str,
    user_id: str = "user-123",
    limit: int = 50
):
    """
    获取报告的版本历史列表

    返回：
    - 版本号、变更类型、变更人、时间等元数据
    - 不包含完整content（节省带宽）
    """
    # 验证权限
    report = Reports.get_report_by_id_and_user_id(report_id, user_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    versions = ReportVersions.get_versions_by_report_id(report_id, limit)
    return versions


@router.get("/{report_id}/versions/{version_number}", response_model=ReportVersionDetail)
async def get_version_detail(
    report_id: str,
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
    report = Reports.get_report_by_id_and_user_id(report_id, user_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    version = ReportVersions.get_version_by_number(report_id, version_number)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    return version


@router.post("/{report_id}/rollback", response_model=ReportResponse)
async def rollback_to_version(
    report_id: str,
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
    report = ReportVersions.rollback_to_version(
        report_id=report_id,
        user_id=user_id,
        version_number=rollback_request.version_number
    )

    if not report:
        raise HTTPException(status_code=404, detail="Rollback failed")

    return report


# ==================== 交互式报告生成 ====================

@router.post("/sessions", response_model=ReportSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_report_session(
    session_data: ReportSessionCreate,
    user_id: str = "user-123"
):
    """
    创建报告生成会话

    流程：
    1. 创建Chat记录（meta.type="report_generation"）
    2. 创建空白Report（关联chat_id）
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
        "type": "report_generation",
        "report_metadata": {
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
            title=f"报告生成：{session_data.topic}",
            chat={},
            meta=chat_meta,
            created_at=int(time.time()),
            updated_at=int(time.time())
        )
        db.add(chat)
        db.commit()

    # 2. 创建报告
    report = Reports.create_report(
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

    if not report:
        raise HTTPException(status_code=500, detail="Failed to create report session")

    # TODO: 启动Blueprint Agent
    # await start_blueprint_agent(thread_id, session_data.topic, ...)

    return ReportSessionResponse(
        chat_id=chat_id,
        report_id=report.id,
        blueprint_thread_id=thread_id,
        topic=session_data.topic
    )


@router.patch("/{report_id}/outline", response_model=ReportResponse)
async def update_report_outline(
    report_id: str,
    outline_update: OutlineUpdateRequest,
    user_id: str = "user-123"
):
    """
    更新报告大纲

    用途：
    - Blueprint Agent生成大纲后更新
    - 用户手动调整章节结构
    - 写作过程中更新章节状态

    注：此操作不创建版本（仅更新outline字段）
    """
    report = Reports.get_report_by_id_and_user_id(report_id, user_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    updated_report = Reports.update_outline(report_id, outline_update.outline)

    if not updated_report:
        raise HTTPException(status_code=500, detail="Failed to update outline")

    return updated_report


# ==================== 会话相关操作 ====================

@router.get("/by-chat/{chat_id}", response_model=ReportResponse)
async def get_report_by_chat_id(
    chat_id: str,
    user_id: str = "user-123"
):
    """根据会话ID获取关联的报告"""
    report = Reports.get_report_by_chat_id(chat_id)

    if not report:
        raise HTTPException(status_code=404, detail="No report found for this chat")

    # 验证权限
    if report.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return report


