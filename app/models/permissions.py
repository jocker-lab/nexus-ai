"""权限模型 - 定义具体的操作权限"""
from app.database.db import Base
from sqlalchemy import BigInteger, Boolean, Column, String, Text, Table, ForeignKey
from sqlalchemy.orm import relationship

# 定义 role_permissions 关联表（用于 secondary 参数）
role_permissions_table = Table(
    "role_permissions",
    Base.metadata,
    Column("id", String(36), primary_key=True),
    Column("role_id", String(36), ForeignKey("role.id", ondelete="CASCADE"), nullable=False),
    Column("permission_id", String(36), ForeignKey("permission.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", BigInteger, nullable=False),
    extend_existing=True
)


class Permission(Base):
    """权限模型 - 定义资源和操作的组合，如 chat:create, report:read"""
    __tablename__ = "permission"

    id = Column(String(36), primary_key=True)
    code = Column(String(100), nullable=False, unique=True, index=True)  # 权限代码，如 "chat:create"
    name = Column(String(100), nullable=False)  # 显示名称
    description = Column(Text, nullable=True)
    resource = Column(String(50), nullable=False, index=True)  # 资源类型，如 "chat", "report"
    action = Column(String(50), nullable=False)  # 操作类型，如 "create", "read", "update", "delete"
    is_active = Column(Boolean, default=True, nullable=False)

    # 时间戳
    created_at = Column(BigInteger, nullable=False)

    # 关联关系
    roles = relationship("Role", secondary=role_permissions_table, back_populates="permissions")
