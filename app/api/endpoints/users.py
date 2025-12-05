"""用户管理 API 端点"""
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.users import User
from app.curd.users import Users
from app.curd.groups import Groups
from app.auth.security import get_password_hash
from app.auth.dependencies import get_current_user
from app.auth.permissions import require_permissions
from app.schemas.auth import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserListResponse,
    MessageResponse,
)

router = APIRouter()


def _user_to_response(user: User) -> UserResponse:
    """转换用户对象为响应"""
    groups = Users.get_user_groups(user.id)
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        profile_image_url=user.profile_image_url,
        is_active=user.is_active,
        is_superadmin=user.is_superadmin,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        groups=[{"id": g.id, "name": g.name} for g in groups]
    )


@router.get("", response_model=UserListResponse)
@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permissions(["user:read"]))
):
    """
    获取用户列表

    需要权限: user:read
    """
    users, total = Users.get_users(
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active
    )

    return UserListResponse(
        items=[_user_to_response(u) for u in users],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_permissions(["user:read"]))
):
    """
    获取用户详情

    需要权限: user:read
    """
    user = Users.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return _user_to_response(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    current_user: User = Depends(require_permissions(["user:manage"]))
):
    """
    创建用户

    需要权限: user:manage
    """
    # 检查邮箱是否已存在
    existing_user = Users.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )

    # 创建用户
    password_hash = get_password_hash(request.password)
    user = Users.create_user(
        name=request.name,
        email=request.email,
        password_hash=password_hash,
        role=request.role,
        is_active=request.is_active,
        is_superadmin=request.is_superadmin
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户失败"
        )

    # 添加到群组
    if request.group_ids:
        Users.update_user_groups(user.id, request.group_ids)
    else:
        # 默认加入用户组
        Users.add_user_to_group(user.id, "group-users")

    return _user_to_response(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    current_user: User = Depends(require_permissions(["user:manage"]))
):
    """
    更新用户

    需要权限: user:manage
    """
    # 检查用户是否存在
    user = Users.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 如果修改邮箱，检查是否已存在
    if request.email and request.email != user.email:
        existing_user = Users.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被使用"
            )

    # 更新用户
    updated_user = Users.update_user(
        user_id=user_id,
        name=request.name,
        email=request.email,
        role=request.role,
        is_active=request.is_active,
        is_superadmin=request.is_superadmin,
        profile_image_url=request.profile_image_url
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户失败"
        )

    # 更新群组
    if request.group_ids is not None:
        Users.update_user_groups(user_id, request.group_ids)

    return _user_to_response(updated_user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_permissions(["user:manage"]))
):
    """
    删除用户

    需要权限: user:manage
    """
    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )

    # 检查用户是否存在
    user = Users.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 不能删除超级管理员
    if user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除超级管理员"
        )

    # 删除用户
    if not Users.delete_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户失败"
        )

    return MessageResponse(message="用户已删除")


@router.post("/{user_id}/reset-password", response_model=MessageResponse)
async def reset_user_password(
    user_id: str,
    new_password: str = Query(..., min_length=8),
    current_user: User = Depends(require_permissions(["user:manage"]))
):
    """
    重置用户密码

    需要权限: user:manage
    """
    user = Users.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 更新密码
    password_hash = get_password_hash(new_password)
    Users.update_password(user_id, password_hash)

    # 撤销所有 Refresh Token
    Users.revoke_all_refresh_tokens(user_id)

    return MessageResponse(message="密码已重置")


@router.post("/{user_id}/toggle-active", response_model=UserResponse)
async def toggle_user_active(
    user_id: str,
    current_user: User = Depends(require_permissions(["user:manage"]))
):
    """
    切换用户激活状态

    需要权限: user:manage
    """
    # 不能停用自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能停用自己"
        )

    user = Users.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 切换状态
    updated_user = Users.update_user(user_id, is_active=not user.is_active)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败"
        )

    # 如果停用，撤销所有 Token
    if not updated_user.is_active:
        Users.revoke_all_refresh_tokens(user_id)

    return _user_to_response(updated_user)
