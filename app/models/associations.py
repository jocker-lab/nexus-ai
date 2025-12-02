"""关联表模型 - 定义多对多关系"""
from app.database.db import Base
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, Text, Table
from sqlalchemy.orm import relationship

# 使用 Table 定义关联表（用于 relationship 的 secondary 参数）
# 这些表通过 extend_existing=True 可以在多个地方引用

UserGroup = Table(
    "user_groups",
    Base.metadata,
    Column("id", String(36), primary_key=True),
    Column("user_id", String(36), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("group_id", String(36), ForeignKey("group.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("created_at", BigInteger, nullable=False),
    extend_existing=True
)

GroupRole = Table(
    "group_roles",
    Base.metadata,
    Column("id", String(36), primary_key=True),
    Column("group_id", String(36), ForeignKey("group.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("role_id", String(36), ForeignKey("role.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("created_at", BigInteger, nullable=False),
    extend_existing=True
)

RolePermission = Table(
    "role_permissions",
    Base.metadata,
    Column("id", String(36), primary_key=True),
    Column("role_id", String(36), ForeignKey("role.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("permission_id", String(36), ForeignKey("permission.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("created_at", BigInteger, nullable=False),
    extend_existing=True
)


class RefreshToken(Base):
    """Refresh Token 存储表 - 用于 Token 刷新和撤销"""
    __tablename__ = "refresh_token"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, index=True)
    device_info = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    expires_at = Column(BigInteger, nullable=False)
    created_at = Column(BigInteger, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)

    # 关联关系
    user = relationship("User", back_populates="refresh_tokens")
