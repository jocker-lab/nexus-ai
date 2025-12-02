"""角色模型 - 包含权限集合"""
from app.database.db import Base
from sqlalchemy import BigInteger, Boolean, Column, String, Text, Table, ForeignKey
from sqlalchemy.orm import relationship

# 定义 group_roles 关联表（用于 secondary 参数）
group_roles_table = Table(
    "group_roles",
    Base.metadata,
    Column("id", String(36), primary_key=True),
    Column("group_id", String(36), ForeignKey("group.id", ondelete="CASCADE"), nullable=False),
    Column("role_id", String(36), ForeignKey("role.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", BigInteger, nullable=False),
    extend_existing=True
)

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


class Role(Base):
    """角色模型 - 角色包含一组权限，可分配给群组"""
    __tablename__ = "role"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)  # 系统角色不可删除
    is_active = Column(Boolean, default=True, nullable=False)

    # 时间戳
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)

    # 关联关系
    groups = relationship("Group", secondary=group_roles_table, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions_table, back_populates="roles")
