"""群组管理 API 端点"""
from typing import Optional, List

from fastapi import APIRouter, HTTPException, status, Depends, Query

from app.models.users import User
from app.curd.groups import Groups
from app.curd.roles import Roles
from app.auth.dependencies import get_current_user
from app.auth.permissions import require_permissions
from app.schemas.groups import (
    GroupCreateRequest,
    GroupUpdateRequest,
    GroupResponse,
    GroupListResponse,
    GroupMemberRequest,
)
from app.schemas.auth import MessageResponse

router = APIRouter()


def _group_to_response(group) -> GroupResponse:
    """转换群组对象为响应"""
    user_count = Groups.get_group_user_count(group.id)
    roles = Groups.get_group_roles(group.id)

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        is_active=group.is_active,
        created_at=group.created_at,
        updated_at=group.updated_at,
        created_by=group.created_by,
        user_count=user_count,
        roles=[{"id": r.id, "name": r.name} for r in roles]
    )


@router.get("", response_model=GroupListResponse)
async def list_groups(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permissions(["group:read"]))
):
    """
    获取群组列表

    需要权限: group:read
    """
    groups, total = Groups.get_groups(
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active
    )

    return GroupListResponse(
        items=[_group_to_response(g) for g in groups],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/all", response_model=List[GroupResponse])
async def list_all_groups(
    is_active: bool = Query(True),
    current_user: User = Depends(require_permissions(["group:read"]))
):
    """
    获取所有群组（不分页）

    需要权限: group:read
    """
    groups = Groups.get_all_groups(is_active=is_active)
    return [_group_to_response(g) for g in groups]


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: str,
    current_user: User = Depends(require_permissions(["group:read"]))
):
    """
    获取群组详情

    需要权限: group:read
    """
    group = Groups.get_group_by_id(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )

    return _group_to_response(group)


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    request: GroupCreateRequest,
    current_user: User = Depends(require_permissions(["group:manage"]))
):
    """
    创建群组

    需要权限: group:manage
    """
    # 检查名称是否已存在
    existing_group = Groups.get_group_by_name(request.name)
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="群组名称已存在"
        )

    # 创建群组
    group = Groups.create_group(
        name=request.name,
        description=request.description,
        created_by=current_user.id
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建群组失败"
        )

    # 添加角色
    if request.role_ids:
        Groups.update_group_roles(group.id, request.role_ids)

    return _group_to_response(group)


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: str,
    request: GroupUpdateRequest,
    current_user: User = Depends(require_permissions(["group:manage"]))
):
    """
    更新群组

    需要权限: group:manage
    """
    group = Groups.get_group_by_id(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )

    # 如果修改名称，检查是否已存在
    if request.name and request.name != group.name:
        existing_group = Groups.get_group_by_name(request.name)
        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="群组名称已存在"
            )

    # 更新群组
    updated_group = Groups.update_group(
        group_id=group_id,
        name=request.name,
        description=request.description,
        is_active=request.is_active
    )

    if not updated_group:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新群组失败"
        )

    # 更新角色
    if request.role_ids is not None:
        Groups.update_group_roles(group_id, request.role_ids)

    return _group_to_response(updated_group)


@router.delete("/{group_id}", response_model=MessageResponse)
async def delete_group(
    group_id: str,
    current_user: User = Depends(require_permissions(["group:manage"]))
):
    """
    删除群组

    需要权限: group:manage
    """
    group = Groups.get_group_by_id(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )

    # 不能删除默认群组
    if group_id in ["group-admins", "group-users"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除系统默认群组"
        )

    if not Groups.delete_group(group_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除群组失败"
        )

    return MessageResponse(message="群组已删除")


@router.post("/{group_id}/members", response_model=MessageResponse)
async def add_group_members(
    group_id: str,
    request: GroupMemberRequest,
    current_user: User = Depends(require_permissions(["group:manage"]))
):
    """
    添加群组成员

    需要权限: group:manage
    """
    group = Groups.get_group_by_id(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )

    added = Groups.add_users_to_group(group_id, request.user_ids)
    return MessageResponse(message=f"已添加 {added} 个成员")


@router.delete("/{group_id}/members", response_model=MessageResponse)
async def remove_group_members(
    group_id: str,
    request: GroupMemberRequest,
    current_user: User = Depends(require_permissions(["group:manage"]))
):
    """
    移除群组成员

    需要权限: group:manage
    """
    group = Groups.get_group_by_id(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )

    removed = Groups.remove_users_from_group(group_id, request.user_ids)
    return MessageResponse(message=f"已移除 {removed} 个成员")


@router.get("/{group_id}/members")
async def get_group_members(
    group_id: str,
    current_user: User = Depends(require_permissions(["group:read"]))
):
    """
    获取群组成员列表

    需要权限: group:read
    """
    group = Groups.get_group_by_id(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )

    users = Groups.get_group_users(group_id)
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "is_active": u.is_active
        }
        for u in users
    ]
