"""群组 CRUD 操作"""
import uuid
import time
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.groups import Group
from app.models.roles import Role
from app.models.users import User
from app.models.associations import UserGroup, GroupRole
from app.database.db import get_db_context


class GroupTable:
    """群组 CRUD 操作类"""

    # ==================== 创建 ====================

    def create_group(
        self,
        name: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Optional[Group]:
        """创建新群组"""
        with get_db_context() as db:
            group_id = str(uuid.uuid4())
            now = int(time.time() * 1000)

            group = Group(
                id=group_id,
                name=name,
                description=description,
                is_active=True,
                created_at=now,
                updated_at=now,
                created_by=created_by
            )

            db.add(group)
            db.commit()
            db.refresh(group)
            return group

    # ==================== 查询 ====================

    def get_group_by_id(self, group_id: str) -> Optional[Group]:
        """根据 ID 获取群组"""
        with get_db_context() as db:
            return db.query(Group).filter(Group.id == group_id).first()

    def get_group_by_name(self, name: str) -> Optional[Group]:
        """根据名称获取群组"""
        with get_db_context() as db:
            return db.query(Group).filter(Group.name == name).first()

    def get_groups(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Group], int]:
        """获取群组列表"""
        with get_db_context() as db:
            query = db.query(Group)

            if search:
                query = query.filter(
                    (Group.name.ilike(f"%{search}%")) |
                    (Group.description.ilike(f"%{search}%"))
                )

            if is_active is not None:
                query = query.filter(Group.is_active == is_active)

            total = query.count()
            groups = query.order_by(Group.created_at.desc())\
                          .offset((page - 1) * page_size)\
                          .limit(page_size)\
                          .all()

            return groups, total

    def get_all_groups(self, is_active: bool = True) -> List[Group]:
        """获取所有群组"""
        with get_db_context() as db:
            query = db.query(Group)
            if is_active:
                query = query.filter(Group.is_active == True)
            return query.order_by(Group.name).all()

    def get_group_users(self, group_id: str) -> List[User]:
        """获取群组成员"""
        with get_db_context() as db:
            # 注意: UserGroup 是 Table 对象，需要用 .c 访问列
            return (
                db.query(User)
                .join(UserGroup, User.id == UserGroup.c.user_id)
                .filter(UserGroup.c.group_id == group_id)
                .all()
            )

    def get_group_user_count(self, group_id: str) -> int:
        """获取群组成员数量"""
        with get_db_context() as db:
            # 注意: UserGroup 是 Table 对象，需要用 .c 访问列
            from sqlalchemy import select, func
            result = db.execute(
                select(func.count()).select_from(UserGroup).where(UserGroup.c.group_id == group_id)
            ).scalar()
            return result or 0

    def get_group_roles(self, group_id: str) -> List[Role]:
        """获取群组角色"""
        with get_db_context() as db:
            # 注意: GroupRole 是 Table 对象，需要用 .c 访问列
            return (
                db.query(Role)
                .join(GroupRole, Role.id == GroupRole.c.role_id)
                .filter(GroupRole.c.group_id == group_id, Role.is_active == True)
                .all()
            )

    # ==================== 更新 ====================

    def update_group(
        self,
        group_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Group]:
        """更新群组信息"""
        with get_db_context() as db:
            group = db.query(Group).filter(Group.id == group_id).first()
            if not group:
                return None

            if name is not None:
                group.name = name
            if description is not None:
                group.description = description
            if is_active is not None:
                group.is_active = is_active

            group.updated_at = int(time.time() * 1000)
            db.commit()
            db.refresh(group)
            return group

    # ==================== 角色管理 ====================

    def add_role_to_group(self, group_id: str, role_id: str) -> bool:
        """添加角色到群组"""
        with get_db_context() as db:
            # 注意: GroupRole 是 Table 对象，需要用 .c 访问列，用 insert() 插入
            from sqlalchemy import select
            # 检查是否已存在
            existing = db.execute(
                select(GroupRole).where(
                    GroupRole.c.group_id == group_id,
                    GroupRole.c.role_id == role_id
                )
            ).first()

            if existing:
                return True

            db.execute(
                GroupRole.insert().values(
                    id=str(uuid.uuid4()),
                    group_id=group_id,
                    role_id=role_id,
                    created_at=int(time.time() * 1000)
                )
            )
            db.commit()
            return True

    def remove_role_from_group(self, group_id: str, role_id: str) -> bool:
        """从群组移除角色"""
        with get_db_context() as db:
            # 注意: GroupRole 是 Table 对象，需要用 .c 访问列
            result = db.execute(
                GroupRole.delete().where(
                    GroupRole.c.group_id == group_id,
                    GroupRole.c.role_id == role_id
                )
            )
            db.commit()
            return result.rowcount > 0

    def update_group_roles(self, group_id: str, role_ids: List[str]) -> bool:
        """更新群组的角色（替换所有）"""
        with get_db_context() as db:
            # 注意: GroupRole 是 Table 对象，需要用 delete()/insert() 操作
            # 删除现有关联
            db.execute(
                GroupRole.delete().where(GroupRole.c.group_id == group_id)
            )

            # 添加新关联
            now = int(time.time() * 1000)
            for role_id in role_ids:
                db.execute(
                    GroupRole.insert().values(
                        id=str(uuid.uuid4()),
                        group_id=group_id,
                        role_id=role_id,
                        created_at=now
                    )
                )

            db.commit()
            return True

    # ==================== 成员管理 ====================

    def add_users_to_group(self, group_id: str, user_ids: List[str]) -> int:
        """批量添加用户到群组"""
        with get_db_context() as db:
            # 注意: UserGroup 是 Table 对象，需要用 .c 访问列，用 insert() 插入
            from sqlalchemy import select
            now = int(time.time() * 1000)
            added = 0

            for user_id in user_ids:
                # 检查是否已存在
                existing = db.execute(
                    select(UserGroup).where(
                        UserGroup.c.user_id == user_id,
                        UserGroup.c.group_id == group_id
                    )
                ).first()

                if not existing:
                    db.execute(
                        UserGroup.insert().values(
                            id=str(uuid.uuid4()),
                            user_id=user_id,
                            group_id=group_id,
                            created_at=now
                        )
                    )
                    added += 1

            db.commit()
            return added

    def remove_users_from_group(self, group_id: str, user_ids: List[str]) -> int:
        """批量从群组移除用户"""
        with get_db_context() as db:
            # 注意: UserGroup 是 Table 对象，需要用 .c 访问列
            result = db.execute(
                UserGroup.delete().where(
                    UserGroup.c.group_id == group_id,
                    UserGroup.c.user_id.in_(user_ids)
                )
            )
            db.commit()
            return result.rowcount

    # ==================== 删除 ====================

    def delete_group(self, group_id: str) -> bool:
        """删除群组"""
        with get_db_context() as db:
            result = db.query(Group).filter(Group.id == group_id).delete()
            db.commit()
            return result > 0


# 全局实例
Groups = GroupTable()
