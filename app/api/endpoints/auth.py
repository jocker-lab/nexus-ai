"""认证 API 端点"""
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.users import User
from app.curd.users import Users
from app.curd.groups import Groups
from app.auth.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    validate_password_strength,
)
from app.auth.config import auth_config
from app.auth.dependencies import get_current_user
from app.auth.permissions import get_user_permissions
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
    UpdateProfileRequest,
    TokenResponse,
    UserInfo,
    UserInfoWithPermissions,
    MessageResponse,
)

router = APIRouter()


def _create_token_response(user: User) -> TokenResponse:
    """创建 Token 响应"""
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    # 存储 Refresh Token
    Users.store_refresh_token(user.id, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=auth_config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserInfo(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            profile_image_url=user.profile_image_url,
            is_superadmin=user.is_superadmin
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    client_request: Request
):
    """
    用户登录

    - 验证邮箱和密码
    - 返回 Access Token 和 Refresh Token
    """
    # 获取用户
    user = Users.get_user_by_email(request.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    # 检查账户是否被锁定
    if Users.is_account_locked(user.id):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"账户已被锁定，请在 {auth_config.LOCKOUT_DURATION_MINUTES} 分钟后重试"
        )

    # 检查账户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账户已被停用"
        )

    # 验证密码
    if not user.password_hash or not verify_password(request.password, user.password_hash):
        Users.increment_failed_attempts(user.id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    # 重置失败次数并更新登录时间
    Users.reset_failed_attempts(user.id)
    Users.update_last_login(user.id)

    return _create_token_response(user)


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """
    用户注册

    - 创建新用户
    - 自动加入默认用户组
    - 返回 Token
    """
    # 验证密码强度
    is_valid, error_msg = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # 检查邮箱是否已注册
    existing_user = Users.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )

    # 创建用户
    password_hash = get_password_hash(request.password)
    user = Users.create_user(
        name=request.name,
        email=request.email,
        password_hash=password_hash,
        role="user"
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户失败"
        )

    # 添加到默认用户组
    Users.add_user_to_group(user.id, "group-users")

    return _create_token_response(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    刷新 Token

    - 验证 Refresh Token
    - 颁发新的 Access Token 和 Refresh Token
    - 撤销旧的 Refresh Token
    """
    # 解码 Token
    payload = decode_token(request.refresh_token)

    if not payload or payload.get("type") != auth_config.TOKEN_TYPE_REFRESH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Refresh Token"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Refresh Token"
        )

    # 验证 Token 是否有效且未被撤销
    if not Users.verify_refresh_token(user_id, request.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token 已失效或被撤销"
        )

    # 获取用户
    user = Users.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已停用"
        )

    # 撤销旧 Token
    Users.revoke_refresh_token(user_id, request.refresh_token)

    # 创建新 Token
    return _create_token_response(user)


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """
    用户登出

    - 撤销所有 Refresh Token
    """
    Users.revoke_all_refresh_tokens(current_user.id)
    return MessageResponse(message="登出成功")


@router.get("/me", response_model=UserInfoWithPermissions)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息

    - 返回用户基本信息、权限和群组
    """
    # 获取权限
    permissions = get_user_permissions(db, current_user.id)

    # 获取群组
    groups = Users.get_user_groups(current_user.id)

    return UserInfoWithPermissions(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        profile_image_url=current_user.profile_image_url,
        is_superadmin=current_user.is_superadmin,
        permissions=list(permissions),
        groups=[{"id": g.id, "name": g.name} for g in groups]
    )


@router.put("/me", response_model=UserInfo)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user)
):
    """
    更新当前用户资料
    """
    updated_user = Users.update_user(
        user_id=current_user.id,
        name=request.name,
        profile_image_url=request.profile_image_url
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败"
        )

    return UserInfo(
        id=updated_user.id,
        name=updated_user.name,
        email=updated_user.email,
        role=updated_user.role,
        profile_image_url=updated_user.profile_image_url,
        is_superadmin=updated_user.is_superadmin
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user)
):
    """
    修改密码
    """
    # 验证当前密码
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )

    # 验证新密码强度
    is_valid, error_msg = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # 更新密码
    new_password_hash = get_password_hash(request.new_password)
    Users.update_password(current_user.id, new_password_hash)

    # 撤销所有 Refresh Token（强制重新登录）
    Users.revoke_all_refresh_tokens(current_user.id)

    return MessageResponse(message="密码修改成功，请重新登录")
