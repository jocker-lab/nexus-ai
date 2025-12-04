"""群组模型 - 用于批量管理用户权限"""
from app.database.db import Base
from sqlalchemy import BigInteger, Boolean, Column, String, Text, Table, ForeignKey
from sqlalchemy.orm import relationship

# 定义 user_groups 关联表（用于 secondary 参数）
user_groups_table = Table(
    "user_groups",
    Base.metadata,
    Column("id", String(36), primary_key=True),
    Column("user_id", String(36), ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
    Column("group_id", String(36), ForeignKey("group.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", BigInteger, nullable=False),
    extend_existing=True
)

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


class Group(Base):
    """群组模型 - 用户可以属于多个群组，群组可以拥有多个角色"""
    __tablename__ = "group"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # 时间戳
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)
    created_by = Column(String(36), nullable=True)

    # 关联关系
    users = relationship("User", secondary=user_groups_table, back_populates="groups")
    roles = relationship("Role", secondary=group_roles_table, back_populates="groups")
