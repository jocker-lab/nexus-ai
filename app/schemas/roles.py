"""角色和权限相关的 Pydantic 模型"""
from typing import Optional, List
from pydantic import BaseModel, Field


# ==================== 权限模型 ====================

class PermissionResponse(BaseModel):
    """权限响应"""
    id: str
    code: str
    name: str
    description: Optional[str] = None
    resource: str
    action: str
    is_active: bool

    class Config:
        from_attributes = True


class PermissionListResponse(BaseModel):
    """权限列表响应"""
    items: List[PermissionResponse]
    total: int


# ==================== 角色模型 ====================

class RoleCreateRequest(BaseModel):
    """创建角色请求"""
    name: str = Field(..., min_length=1, max_length=100, description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")
    permission_ids: List[str] = Field(default=[], description="权限 ID 列表")


class RoleUpdateRequest(BaseModel):
    """更新角色请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[str]] = None


class RoleResponse(BaseModel):
    """角色响应"""
    id: str
    name: str
    description: Optional[str] = None
    is_system: bool
    is_active: bool
    created_at: int
    updated_at: int
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    """角色列表响应"""
    items: List[RoleResponse]
    total: int
    page: int
    page_size: int


class RolePermissionRequest(BaseModel):
    """角色权限操作请求"""
    permission_ids: List[str] = Field(..., description="权限 ID 列表")
