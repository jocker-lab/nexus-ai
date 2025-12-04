"""认证相关的 Pydantic 模型"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ==================== 请求模型 ====================

class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=1, description="密码")


class RegisterRequest(BaseModel):
    """注册请求"""
    name: str = Field(..., min_length=1, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=8, description="密码（至少8位）")


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str = Field(..., description="Refresh Token")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=8, description="新密码（至少8位）")


class UpdateProfileRequest(BaseModel):
    """更新个人资料请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="用户名")
    profile_image_url: Optional[str] = Field(None, description="头像 URL")


# ==================== 响应模型 ====================

class UserInfo(BaseModel):
    """用户基本信息"""
    id: str
    name: Optional[str] = None
    email: str
    role: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_superadmin: bool = False

    class Config:
        from_attributes = True


class UserInfoWithPermissions(UserInfo):
    """用户信息（包含权限）"""
    permissions: List[str] = []
    groups: List[dict] = []


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access Token 过期时间（秒）")
    user: UserInfo


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    success: bool = True


# ==================== 用户管理模型 ====================

class UserCreateRequest(BaseModel):
    """创建用户请求（管理员）"""
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(default="user")
    is_active: bool = Field(default=True)
    is_superadmin: bool = Field(default=False)
    group_ids: List[str] = Field(default=[])


class UserUpdateRequest(BaseModel):
    """更新用户请求（管理员）"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_superadmin: Optional[bool] = None
    profile_image_url: Optional[str] = None
    group_ids: Optional[List[str]] = None


class UserResponse(BaseModel):
    """用户详情响应"""
    id: str
    name: Optional[str] = None
    email: str
    role: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: bool
    is_superadmin: bool
    last_login_at: Optional[int] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    groups: List[dict] = []

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    items: List[UserResponse]
    total: int
    page: int
    page_size: int
