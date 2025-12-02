import time
from typing import Optional, List, TYPE_CHECKING
from app.database.db import Base
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Boolean, Column, String, Text, Integer, Table, ForeignKey
from sqlalchemy.dialects.mysql import MEDIUMTEXT, JSON
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


class User(Base):
    """用户模型 - 包含认证和基本信息"""
    __tablename__ = "user"

    # 基本信息
    id = Column(String(36), primary_key=True)
    name = Column(String(50))
    email = Column(String(50), unique=True, index=True)
    role = Column(String(50))
    profile_image_url = Column(Text)

    # 认证字段
    password_hash = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superadmin = Column(Boolean, default=False, nullable=False)

    # 安全字段
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(BigInteger, nullable=True)
    last_login_at = Column(BigInteger, nullable=True)

    # 时间戳
    last_active_at = Column(BigInteger)
    updated_at = Column(BigInteger)
    created_at = Column(BigInteger)

    # API 和 OAuth
    api_key = Column(String(255), nullable=True, unique=True)
    settings = Column(JSON, nullable=True)
    info = Column(JSON, nullable=True)
    oauth_sub = Column(Text, unique=True)

    # 关联关系
    groups = relationship("Group", secondary=user_groups_table, back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")