"""权限检查 - RBAC 权限验证装饰器和工具"""
from functools import wraps
from typing import List, Callable, Set

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.users import User
from app.models.permissions import Permission
from app.models.roles import Role
from app.models.groups import Group
from app.models.associations import UserGroup, GroupRole, RolePermission

from .dependencies import get_current_user


def get_user_permissions(db: Session, user_id: str) -> Set[str]:
    """
    获取用户所有权限代码

    通过 User -> Groups -> Roles -> Permissions 链路获取所有权限。

    Args:
        db: 数据库会话
        user_id: 用户 ID

    Returns:
        权限代码集合，如 {"chat:create", "report:read"}
    """
    # 查询用户所属群组的所有权限
    # 注意: UserGroup, GroupRole, RolePermission 是 Table 对象，需要用 .c 访问列
    permissions = (
        db.query(Permission.code)
        .join(RolePermission, Permission.id == RolePermission.c.permission_id)
        .join(Role, RolePermission.c.role_id == Role.id)
        .join(GroupRole, Role.id == GroupRole.c.role_id)
        .join(Group, GroupRole.c.group_id == Group.id)
        .join(UserGroup, Group.id == UserGroup.c.group_id)
        .filter(
            UserGroup.c.user_id == user_id,
            Permission.is_active == True,
            Role.is_active == True,
            Group.is_active == True
        )
        .distinct()
        .all()
    )

    return {p.code for p in permissions}


def check_permissions(
    user: User,
    required_permissions: List[str],
    db: Session
) -> bool:
    """
    检查用户是否拥有所需权限

    Args:
        user: 用户对象
        required_permissions: 所需权限代码列表
        db: 数据库会话

    Returns:
        是否拥有所有所需权限
    """
    # 超级管理员拥有所有权限
    if user.is_superadmin:
        return True

    # 获取用户权限
    user_permissions = get_user_permissions(db, user.id)

    # 检查是否拥有所有所需权限
    return all(perm in user_permissions for perm in required_permissions)


def require_permissions(required_permissions: List[str]):
    """
    权限检查依赖注入工厂

    用法:
        @router.get("/admin/users")
        async def list_users(
            current_user: User = Depends(require_permissions(["user:read"]))
        ):
            ...

    Args:
        required_permissions: 所需权限代码列表

    Returns:
        FastAPI 依赖函数
    """
    async def permission_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # 超级管理员直接通过
        if current_user.is_superadmin:
            return current_user

        # 获取用户权限
        user_permissions = get_user_permissions(db, current_user.id)

        # 检查是否拥有所有所需权限
        missing_permissions = [
            perm for perm in required_permissions
            if perm not in user_permissions
        ]

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {', '.join(missing_permissions)}"
            )

        return current_user

    return permission_dependency


def require_any_permission(required_permissions: List[str]):
    """
    权限检查依赖注入工厂（满足任一权限即可）

    Args:
        required_permissions: 权限代码列表（满足任一即可）

    Returns:
        FastAPI 依赖函数
    """
    async def permission_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # 超级管理员直接通过
        if current_user.is_superadmin:
            return current_user

        # 获取用户权限
        user_permissions = get_user_permissions(db, current_user.id)

        # 检查是否拥有任一所需权限
        has_permission = any(
            perm in user_permissions
            for perm in required_permissions
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下任一权限: {', '.join(required_permissions)}"
            )

        return current_user

    return permission_dependency


class PermissionChecker:
    """
    权限检查器类

    支持作为 FastAPI 依赖使用，提供更灵活的权限检查。

    用法:
        permission_checker = PermissionChecker(["user:read", "user:manage"])

        @router.get("/users")
        async def list_users(user: User = Depends(permission_checker)):
            ...
    """

    def __init__(self, required_permissions: List[str], require_all: bool = True):
        """
        Args:
            required_permissions: 所需权限代码列表
            require_all: True 表示需要所有权限，False 表示满足任一即可
        """
        self.required_permissions = required_permissions
        self.require_all = require_all

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # 超级管理员直接通过
        if current_user.is_superadmin:
            return current_user

        # 获取用户权限
        user_permissions = get_user_permissions(db, current_user.id)

        if self.require_all:
            # 需要所有权限
            missing = [p for p in self.required_permissions if p not in user_permissions]
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少权限: {', '.join(missing)}"
                )
        else:
            # 满足任一权限即可
            has_any = any(p in user_permissions for p in self.required_permissions)
            if not has_any:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"需要以下任一权限: {', '.join(self.required_permissions)}"
                )

        return current_user
