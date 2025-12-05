"""角色和权限管理 API 端点"""
from typing import Optional, List

from fastapi import APIRouter, HTTPException, status, Depends, Query

from app.models.users import User
from app.curd.roles import Roles, Permissions
from app.auth.dependencies import get_current_user
from app.auth.permissions import require_permissions
from app.schemas.roles import (
    RoleCreateRequest,
    RoleUpdateRequest,
    RoleResponse,
    RoleListResponse,
    RolePermissionRequest,
    PermissionResponse,
    PermissionListResponse,
)
from app.schemas.auth import MessageResponse

router = APIRouter()


def _role_to_response(role) -> RoleResponse:
    """转换角色对象为响应"""
    permissions = Roles.get_role_permissions(role.id)

    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        is_system=role.is_system,
        is_active=role.is_active,
        created_at=role.created_at,
        updated_at=role.updated_at,
        permissions=[
            PermissionResponse(
                id=p.id,
                code=p.code,
                name=p.name,
                description=p.description,
                resource=p.resource,
                action=p.action,
                is_active=p.is_active
            )
            for p in permissions
        ]
    )


# ==================== 角色管理 ====================

@router.get("", response_model=RoleListResponse)
@router.get("/", response_model=RoleListResponse)
async def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permissions(["role:read"]))
):
    """
    获取角色列表

    需要权限: role:read
    """
    roles, total = Roles.get_roles(
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active
    )

    return RoleListResponse(
        items=[_role_to_response(r) for r in roles],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/all", response_model=List[RoleResponse])
async def list_all_roles(
    is_active: bool = Query(True),
    current_user: User = Depends(require_permissions(["role:read"]))
):
    """
    获取所有角色（不分页）

    需要权限: role:read
    """
    roles = Roles.get_all_roles(is_active=is_active)
    return [_role_to_response(r) for r in roles]


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    current_user: User = Depends(require_permissions(["role:read"]))
):
    """
    获取角色详情

    需要权限: role:read
    """
    role = Roles.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )

    return _role_to_response(role)


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    request: RoleCreateRequest,
    current_user: User = Depends(require_permissions(["role:manage"]))
):
    """
    创建角色

    需要权限: role:manage
    """
    # 检查名称是否已存在
    existing_role = Roles.get_role_by_name(request.name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色名称已存在"
        )

    # 创建角色
    role = Roles.create_role(
        name=request.name,
        description=request.description,
        is_system=False
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建角色失败"
        )

    # 添加权限
    if request.permission_ids:
        Roles.update_role_permissions(role.id, request.permission_ids)

    return _role_to_response(role)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    request: RoleUpdateRequest,
    current_user: User = Depends(require_permissions(["role:manage"]))
):
    """
    更新角色

    需要权限: role:manage
    """
    role = Roles.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )

    # 系统角色不能修改名称
    if role.is_system and request.name and request.name != role.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="系统角色不能修改名称"
        )

    # 如果修改名称，检查是否已存在
    if request.name and request.name != role.name:
        existing_role = Roles.get_role_by_name(request.name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色名称已存在"
            )

    # 更新角色
    updated_role = Roles.update_role(
        role_id=role_id,
        name=request.name,
        description=request.description,
        is_active=request.is_active
    )

    if not updated_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新角色失败"
        )

    # 更新权限
    if request.permission_ids is not None:
        Roles.update_role_permissions(role_id, request.permission_ids)

    return _role_to_response(updated_role)


@router.delete("/{role_id}", response_model=MessageResponse)
async def delete_role(
    role_id: str,
    current_user: User = Depends(require_permissions(["role:manage"]))
):
    """
    删除角色

    需要权限: role:manage
    """
    role = Roles.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )

    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="系统角色不能删除"
        )

    if not Roles.delete_role(role_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除角色失败"
        )

    return MessageResponse(message="角色已删除")


@router.put("/{role_id}/permissions", response_model=RoleResponse)
async def update_role_permissions(
    role_id: str,
    request: RolePermissionRequest,
    current_user: User = Depends(require_permissions(["role:manage"]))
):
    """
    更新角色权限

    需要权限: role:manage
    """
    role = Roles.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )

    Roles.update_role_permissions(role_id, request.permission_ids)

    return _role_to_response(role)


# ==================== 权限管理 ====================

@router.get("/permissions/all", response_model=PermissionListResponse)
async def list_all_permissions(
    current_user: User = Depends(require_permissions(["role:read"]))
):
    """
    获取所有权限

    需要权限: role:read
    """
    permissions = Permissions.get_all_permissions()

    return PermissionListResponse(
        items=[
            PermissionResponse(
                id=p.id,
                code=p.code,
                name=p.name,
                description=p.description,
                resource=p.resource,
                action=p.action,
                is_active=p.is_active
            )
            for p in permissions
        ],
        total=len(permissions)
    )


@router.get("/permissions/by-resource/{resource}", response_model=List[PermissionResponse])
async def get_permissions_by_resource(
    resource: str,
    current_user: User = Depends(require_permissions(["role:read"]))
):
    """
    根据资源获取权限

    需要权限: role:read
    """
    permissions = Permissions.get_permissions_by_resource(resource)

    return [
        PermissionResponse(
            id=p.id,
            code=p.code,
            name=p.name,
            description=p.description,
            resource=p.resource,
            action=p.action,
            is_active=p.is_active
        )
        for p in permissions
    ]
