from typing import Optional
from pydantic import BaseModel, ConfigDict

class TagModel(BaseModel):
    id: str
    name: str
    user_id: str
    meta: Optional[dict] = None
    model_config = ConfigDict(from_attributes=True)



class TagChatIdForm(BaseModel):
    name: str
    chat_id: str
