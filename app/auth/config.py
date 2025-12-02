"""认证配置 - JWT 和安全设置"""
import os
import secrets
from pydantic import BaseModel, Field


class AuthConfig(BaseModel):
    """认证配置类"""

    # JWT 配置
    SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32)),
        description="JWT 签名密钥"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT 加密算法")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        description="Access Token 过期时间（分钟）"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")),
        description="Refresh Token 过期时间（天）"
    )

    # 密码策略
    PASSWORD_MIN_LENGTH: int = Field(default=8, description="密码最小长度")

    # 账户安全
    MAX_FAILED_ATTEMPTS: int = Field(default=5, description="最大登录失败次数")
    LOCKOUT_DURATION_MINUTES: int = Field(default=30, description="账户锁定时间（分钟）")

    # Token 类型标识
    TOKEN_TYPE_ACCESS: str = "access"
    TOKEN_TYPE_REFRESH: str = "refresh"


# 全局配置实例
auth_config = AuthConfig()
