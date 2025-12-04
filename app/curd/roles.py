"""角色和权限 CRUD 操作"""
import uuid
import time
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session

from app.models.roles import Role
from app.models.permissions import Permission
from app.models.associations import RolePermission, GroupRole
from app.database.db import get_db_context


class RoleTable:
    """角色 CRUD 操作类"""

    # ==================== 创建 ====================

    def create_role(
        self,
        name: str,
        description: Optional[str] = None,
        is_system: bool = False
    ) -> Optional[Role]:
        """创建新角色"""
        with get_db_context() as db:
            role_id = str(uuid.uuid4())
            now = int(time.time() * 1000)

            role = Role(
                id=role_id,
                name=name,
                description=description,
                is_system=is_system,
                is_active=True,
                created_at=now,
                updated_at=now
            )

            db.add(role)
            db.commit()
            db.refresh(role)
            return role

    # ==================== 查询 ====================

    def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """根据 ID 获取角色"""
        with get_db_context() as db:
            return db.query(Role).filter(Role.id == role_id).first()

    def get_role_by_name(self, name: str) -> Optional[Role]:
        """根据名称获取角色"""
        with get_db_context() as db:
            return db.query(Role).filter(Role.name == name).first()

    def get_roles(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Role], int]:
        """获取角色列表"""
        with get_db_context() as db:
            query = db.query(Role)

            if search:
                query = query.filter(
                    (Role.name.ilike(f"%{search}%")) |
                    (Role.description.ilike(f"%{search}%"))
                )

            if is_active is not None:
                query = query.filter(Role.is_active == is_active)

            total = query.count()
            roles = query.order_by(Role.created_at.desc())\
                         .offset((page - 1) * page_size)\
                         .limit(page_size)\
                         .all()

            return roles, total

    def get_all_roles(self, is_active: bool = True) -> List[Role]:
        """获取所有角色"""
        with get_db_context() as db:
            query = db.query(Role)
            if is_active:
                query = query.filter(Role.is_active == True)
            return query.order_by(Role.name).all()

    def get_role_permissions(self, role_id: str) -> List[Permission]:
        """获取角色权限"""
        with get_db_context() as db:
            # 注意: RolePermission 是 Table 对象，需要用 .c 访问列
            return (
                db.query(Permission)
                .join(RolePermission, Permission.id == RolePermission.c.permission_id)
                .filter(RolePermission.c.role_id == role_id, Permission.is_active == True)
                .all()
            )

    # ==================== 更新 ====================

    def update_role(
        self,
        role_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Role]:
        """更新角色信息"""
        with get_db_context() as db:
            role = db.query(Role).filter(Role.id == role_id).first()
            if not role:
                return None

            # 系统角色不能修改名称
            if role.is_system and name is not None and name != role.name:
                return None

            if name is not None:
                role.name = name
            if description is not None:
                role.description = description
            if is_active is not None:
                role.is_active = is_active

            role.updated_at = int(time.time() * 1000)
            db.commit()
            db.refresh(role)
            return role

    # ==================== 权限管理 ====================

    def add_permission_to_role(self, role_id: str, permission_id: str) -> bool:
        """添加权限到角色"""
        with get_db_context() as db:
            # 注意: RolePermission 是 Table 对象，需要用 .c 访问列，用 insert() 插入
            # 检查是否已存在
            from sqlalchemy import select
            existing = db.execute(
                select(RolePermission).where(
                    RolePermission.c.role_id == role_id,
                    RolePermission.c.permission_id == permission_id
                )
            ).first()

            if existing:
                return True

            db.execute(
                RolePermission.insert().values(
                    id=str(uuid.uuid4()),
                    role_id=role_id,
                    permission_id=permission_id,
                    created_at=int(time.time() * 1000)
                )
            )
            db.commit()
            return True

    def remove_permission_from_role(self, role_id: str, permission_id: str) -> bool:
        """从角色移除权限"""
        with get_db_context() as db:
            # 注意: RolePermission 是 Table 对象，需要用 .c 访问列
            result = db.execute(
                RolePermission.delete().where(
                    RolePermission.c.role_id == role_id,
                    RolePermission.c.permission_id == permission_id
                )
            )
            db.commit()
            return result.rowcount > 0

    def update_role_permissions(self, role_id: str, permission_ids: List[str]) -> bool:
        """更新角色的权限（替换所有）"""
        with get_db_context() as db:
            # 注意: RolePermission 是 Table 对象，需要用 delete()/insert() 操作
            # 删除现有关联
            db.execute(
                RolePermission.delete().where(RolePermission.c.role_id == role_id)
            )

            # 添加新关联
            now = int(time.time() * 1000)
            for permission_id in permission_ids:
                db.execute(
                    RolePermission.insert().values(
                        id=str(uuid.uuid4()),
                        role_id=role_id,
                        permission_id=permission_id,
                        created_at=now
                    )
                )

            db.commit()
            return True

    # ==================== 删除 ====================

    def delete_role(self, role_id: str) -> bool:
        """删除角色（系统角色不可删除）"""
        with get_db_context() as db:
            role = db.query(Role).filter(Role.id == role_id).first()
            if not role or role.is_system:
                return False

            db.query(Role).filter(Role.id == role_id).delete()
            db.commit()
            return True


class PermissionTable:
    """权限 CRUD 操作类"""

    def get_permission_by_id(self, permission_id: str) -> Optional[Permission]:
        """根据 ID 获取权限"""
        with get_db_context() as db:
            return db.query(Permission).filter(Permission.id == permission_id).first()

    def get_permission_by_code(self, code: str) -> Optional[Permission]:
        """根据代码获取权限"""
        with get_db_context() as db:
            return db.query(Permission).filter(Permission.code == code).first()

    def get_all_permissions(self, is_active: bool = True) -> List[Permission]:
        """获取所有权限"""
        with get_db_context() as db:
            query = db.query(Permission)
            if is_active:
                query = query.filter(Permission.is_active == True)
            return query.order_by(Permission.resource, Permission.action).all()

    def get_permissions_by_resource(self, resource: str) -> List[Permission]:
        """根据资源获取权限"""
        with get_db_context() as db:
            return (
                db.query(Permission)
                .filter(Permission.resource == resource, Permission.is_active == True)
                .order_by(Permission.action)
                .all()
            )


# 全局实例
Roles = RoleTable()
Permissions = PermissionTable()
