"""群组相关的 Pydantic 模型"""
from typing import Optional, List
from pydantic import BaseModel, Field


class GroupCreateRequest(BaseModel):
    """创建群组请求"""
    name: str = Field(..., min_length=1, max_length=100, description="群组名称")
    description: Optional[str] = Field(None, description="群组描述")
    role_ids: List[str] = Field(default=[], description="角色 ID 列表")


class GroupUpdateRequest(BaseModel):
    """更新群组请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[str]] = None


class GroupResponse(BaseModel):
    """群组响应"""
    id: str
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: int
    updated_at: int
    created_by: Optional[str] = None
    user_count: int = 0
    roles: List[dict] = []

    class Config:
        from_attributes = True


class GroupListResponse(BaseModel):
    """群组列表响应"""
    items: List[GroupResponse]
    total: int
    page: int
    page_size: int


class GroupMemberRequest(BaseModel):
    """群组成员操作请求"""
    user_ids: List[str] = Field(..., description="用户 ID 列表")
