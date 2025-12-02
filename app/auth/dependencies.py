"""FastAPI 依赖注入 - 用户认证和权限检查"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database.db import get_db
from app.models.users import User
from sqlalchemy.orm import Session

from .config import auth_config
from .security import decode_token

# HTTP Bearer Token 提取器
security = HTTPBearer(auto_error=False)
security_required = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_required),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前认证用户（必须认证）

    从 Authorization 头中提取 Bearer Token，验证并返回用户对象。

    Raises:
        HTTPException 401: Token 无效或过期
        HTTPException 401: 用户不存在或已停用
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise credentials_exception

    # 验证 Token 类型
    if payload.get("type") != auth_config.TOKEN_TYPE_ACCESS:
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户账户已停用"
        )

    return user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    获取当前用户（可选认证）

    如果提供了有效 Token 则返回用户，否则返回 None。
    用于支持匿名访问的端点。
    """
    if not credentials:
        return None

    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != auth_config.TOKEN_TYPE_ACCESS:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        return None

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户

    确保用户账户处于活跃状态。
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已停用"
        )
    return current_user


async def get_current_superadmin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前超级管理员

    确保当前用户是超级管理员。
    """
    if not current_user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限"
        )
    return current_user
