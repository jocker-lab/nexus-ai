"""
初始化默认 Admin 用户

应用启动时自动检测并创建默认管理员账户。
"""
import os
from loguru import logger
from sqlalchemy.orm import Session

from app.models.users import User
from app.models.groups import Group
from app.models.associations import UserGroup
from app.auth.security import get_password_hash
import time
import uuid


# 默认 admin 配置（可通过环境变量覆盖）
DEFAULT_ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "pygao.1@outlook.com")
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")


def init_default_admin(db: Session) -> bool:
    """
    初始化默认管理员用户

    Returns:
        bool: True 如果创建了新用户，False 如果已存在
    """
    # 检查是否已存在 admin 用户（按邮箱或 superadmin 标志）
    existing_admin = db.query(User).filter(
        (User.email == DEFAULT_ADMIN_EMAIL) | (User.is_superadmin == True)
    ).first()

    if existing_admin:
        logger.info(f"Admin user already exists: {existing_admin.email}")
        return False

    now = int(time.time() * 1000)

    # 创建 admin 用户
    admin_user = User(
        id=str(uuid.uuid4()),
        name=DEFAULT_ADMIN_USERNAME,
        email=DEFAULT_ADMIN_EMAIL,
        password_hash=get_password_hash(DEFAULT_ADMIN_PASSWORD),
        is_active=True,
        is_superadmin=True,
        created_at=now,
        updated_at=now,
    )

    db.add(admin_user)
    db.flush()  # 获取 user id

    # 将 admin 加入 Administrators 组
    admin_group = db.query(Group).filter(Group.name == "Administrators").first()
    if admin_group:
        # UserGroup 是 Table 对象，使用 insert 语句
        db.execute(
            UserGroup.insert().values(
                id=str(uuid.uuid4()),
                user_id=admin_user.id,
                group_id=admin_group.id,
                created_at=now,
            )
        )

    db.commit()

    logger.info(f"Created default admin user: {DEFAULT_ADMIN_EMAIL}")
    logger.warning(
        f"⚠️  Default admin credentials - Email: {DEFAULT_ADMIN_EMAIL}, "
        f"Password: {DEFAULT_ADMIN_PASSWORD}"
    )
    logger.warning("⚠️  Please change the default password after first login!")

    return True


def ensure_admin_exists(db: Session) -> None:
    """
    确保系统中存在至少一个管理员用户
    在应用启动时调用
    """
    try:
        init_default_admin(db)
    except Exception as e:
        logger.error(f"Failed to initialize admin user: {e}")
        # 不抛出异常，允许应用继续启动
