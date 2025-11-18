from pydantic import BaseModel, ConfigDict
from typing import Optional

# 定义数据模型
class FolderModel(BaseModel):
    id: str
    parent_id: Optional[str] = None
    user_id: str
    name: str
    items: Optional[dict] = None
    meta: Optional[dict] = None
    is_expanded: bool = False
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)

# 定义请求的数据模型
class FolderForm(BaseModel):
    name: str
    model_config = ConfigDict(extra="allow")


class FolderParentIdForm(BaseModel):
    parent_id: Optional[str] = None


class FolderIsExpandedForm(BaseModel):
    is_expanded: bool