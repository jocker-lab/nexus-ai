"""用户 CRUD 操作"""
import uuid
import time
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.users import User
from app.models.groups import Group
from app.models.permissions import Permission
from app.models.associations import UserGroup, GroupRole, RolePermission, RefreshToken
from app.auth.security import get_password_hash, hash_token, verify_password
from app.auth.config import auth_config
from app.database.db import get_db_context


class UserTable:
    """用户 CRUD 操作类"""

    # ==================== 创建 ====================

    def create_user(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: str = "user",
        is_active: bool = True,
        is_superadmin: bool = False
    ) -> Optional[User]:
        """创建新用户"""
        with get_db_context() as db:
            user_id = str(uuid.uuid4())
            now = int(time.time() * 1000)

            user = User(
                id=user_id,
                name=name,
                email=email,
                password_hash=password_hash,
                role=role,
                is_active=is_active,
                is_superadmin=is_superadmin,
                created_at=now,
                updated_at=now
            )

            db.add(user)
            db.commit()
            db.refresh(user)
            return user

    # ==================== 查询 ====================

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据 ID 获取用户"""
        with get_db_context() as db:
            return db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        with get_db_context() as db:
            return db.query(User).filter(User.email == email).first()

    def get_users(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """获取用户列表"""
        with get_db_context() as db:
            query = db.query(User)

            if search:
                query = query.filter(
                    (User.name.ilike(f"%{search}%")) |
                    (User.email.ilike(f"%{search}%"))
                )

            if is_active is not None:
                query = query.filter(User.is_active == is_active)

            total = query.count()
            users = query.order_by(User.created_at.desc())\
                         .offset((page - 1) * page_size)\
                         .limit(page_size)\
                         .all()

            return users, total

    def get_user_groups(self, user_id: str) -> List[Group]:
        """获取用户所属群组"""
        with get_db_context() as db:
            # 注意: UserGroup 是 Table 对象，需要用 .c 访问列
            return (
                db.query(Group)
                .join(UserGroup, Group.id == UserGroup.c.group_id)
                .filter(UserGroup.c.user_id == user_id, Group.is_active == True)
                .all()
            )

    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """获取用户所有权限"""
        with get_db_context() as db:
            # 注意: UserGroup, GroupRole, RolePermission 是 Table 对象，需要用 .c 访问列
            return (
                db.query(Permission)
                .join(RolePermission, Permission.id == RolePermission.c.permission_id)
                .join(GroupRole, RolePermission.c.role_id == GroupRole.c.role_id)
                .join(UserGroup, GroupRole.c.group_id == UserGroup.c.group_id)
                .filter(
                    UserGroup.c.user_id == user_id,
                    Permission.is_active == True
                )
                .distinct()
                .all()
            )

    # ==================== 更新 ====================

    def update_user(
        self,
        user_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superadmin: Optional[bool] = None,
        profile_image_url: Optional[str] = None
    ) -> Optional[User]:
        """更新用户信息"""
        with get_db_context() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            if name is not None:
                user.name = name
            if email is not None:
                user.email = email
            if role is not None:
                user.role = role
            if is_active is not None:
                user.is_active = is_active
            if is_superadmin is not None:
                user.is_superadmin = is_superadmin
            if profile_image_url is not None:
                user.profile_image_url = profile_image_url

            user.updated_at = int(time.time() * 1000)
            db.commit()
            db.refresh(user)
            return user

    def update_password(self, user_id: str, new_password_hash: str) -> bool:
        """更新用户密码"""
        with get_db_context() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            user.password_hash = new_password_hash
            user.updated_at = int(time.time() * 1000)
            db.commit()
            return True

    def update_last_login(self, user_id: str) -> bool:
        """更新最后登录时间"""
        with get_db_context() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            user.last_login_at = int(time.time() * 1000)
            db.commit()
            return True

    # ==================== 登录安全 ====================

    def increment_failed_attempts(self, user_id: str) -> bool:
        """增加登录失败次数"""
        with get_db_context() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            user.failed_login_attempts += 1

            # 超过最大次数则锁定账户
            if user.failed_login_attempts >= auth_config.MAX_FAILED_ATTEMPTS:
                user.locked_until = int(time.time() * 1000) + \
                    (auth_config.LOCKOUT_DURATION_MINUTES * 60 * 1000)

            db.commit()
            return True

    def reset_failed_attempts(self, user_id: str) -> bool:
        """重置登录失败次数"""
        with get_db_context() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            user.failed_login_attempts = 0
            user.locked_until = None
            db.commit()
            return True

    def is_account_locked(self, user_id: str) -> bool:
        """检查账户是否被锁定"""
        with get_db_context() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.locked_until:
                return False

            return user.locked_until > int(time.time() * 1000)

    # ==================== Refresh Token ====================

    def store_refresh_token(
        self,
        user_id: str,
        token: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        """存储 Refresh Token"""
        with get_db_context() as db:
            now = int(time.time() * 1000)
            expires_at = now + (auth_config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60 * 1000)

            refresh_token = RefreshToken(
                id=str(uuid.uuid4()),
                user_id=user_id,
                token_hash=hash_token(token),
                device_info=device_info,
                ip_address=ip_address,
                expires_at=expires_at,
                created_at=now,
                is_revoked=False
            )

            db.add(refresh_token)
            db.commit()
            return True

    def verify_refresh_token(self, user_id: str, token: str) -> bool:
        """验证 Refresh Token"""
        with get_db_context() as db:
            token_hash = hash_token(token)
            now = int(time.time() * 1000)

            refresh_token = (
                db.query(RefreshToken)
                .filter(
                    RefreshToken.user_id == user_id,
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.is_revoked == False,
                    RefreshToken.expires_at > now
                )
                .first()
            )

            return refresh_token is not None

    def revoke_refresh_token(self, user_id: str, token: str) -> bool:
        """撤销 Refresh Token"""
        with get_db_context() as db:
            token_hash = hash_token(token)

            result = (
                db.query(RefreshToken)
                .filter(
                    RefreshToken.user_id == user_id,
                    RefreshToken.token_hash == token_hash
                )
                .update({"is_revoked": True})
            )

            db.commit()
            return result > 0

    def revoke_all_refresh_tokens(self, user_id: str) -> bool:
        """撤销用户所有 Refresh Token"""
        with get_db_context() as db:
            db.query(RefreshToken)\
              .filter(RefreshToken.user_id == user_id)\
              .update({"is_revoked": True})
            db.commit()
            return True

    # ==================== 群组管理 ====================

    def add_user_to_group(self, user_id: str, group_id: str) -> bool:
        """添加用户到群组"""
        with get_db_context() as db:
            # 注意: UserGroup 是 Table 对象，需要用 .c 访问列，用 insert() 插入
            from sqlalchemy import select
            # 检查是否已存在
            existing = db.execute(
                select(UserGroup).where(
                    UserGroup.c.user_id == user_id,
                    UserGroup.c.group_id == group_id
                )
            ).first()

            if existing:
                return True

            db.execute(
                UserGroup.insert().values(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    group_id=group_id,
                    created_at=int(time.time() * 1000)
                )
            )
            db.commit()
            return True

    def remove_user_from_group(self, user_id: str, group_id: str) -> bool:
        """从群组移除用户"""
        with get_db_context() as db:
            # 注意: UserGroup 是 Table 对象，需要用 .c 访问列
            result = db.execute(
                UserGroup.delete().where(
                    UserGroup.c.user_id == user_id,
                    UserGroup.c.group_id == group_id
                )
            )
            db.commit()
            return result.rowcount > 0

    def update_user_groups(self, user_id: str, group_ids: List[str]) -> bool:
        """更新用户的群组（替换所有）"""
        with get_db_context() as db:
            # 注意: UserGroup 是 Table 对象，需要用 delete()/insert() 操作
            # 删除现有关联
            db.execute(
                UserGroup.delete().where(UserGroup.c.user_id == user_id)
            )

            # 添加新关联
            now = int(time.time() * 1000)
            for group_id in group_ids:
                db.execute(
                    UserGroup.insert().values(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        group_id=group_id,
                        created_at=now
                    )
                )

            db.commit()
            return True

    # ==================== 删除 ====================

    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        with get_db_context() as db:
            result = db.query(User).filter(User.id == user_id).delete()
            db.commit()
            return result > 0


# 全局实例
Users = UserTable()
