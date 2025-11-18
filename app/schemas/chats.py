from typing import Optional
from pydantic import BaseModel, ConfigDict



class ChatModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    chat: dict

    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch

    archived: bool = False

    pinned: Optional[bool] = False

    meta: dict = {}
    folder_id: Optional[str] = None


class ChatForm(BaseModel):
    chat: dict

class ChatTitleMessagesForm(BaseModel):
    title: str
    messages: list[dict]

class ChatTitleForm(BaseModel):
    title: str


class ChatResponse(BaseModel):
    id: str
    user_id: str
    title: str
    chat: dict
    updated_at: int  # timestamp in epoch
    created_at: int  # timestamp in epoch

    pinned: Optional[bool] = False
    meta: dict = {}
    folder_id: Optional[str] = None

class ChatTitleIdResponse(BaseModel):
    id: str
    title: str
    pinned: bool
    updated_at: int
    created_at: int


