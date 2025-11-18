from app.database.db import Base
from sqlalchemy import BigInteger, Boolean, Column, String, Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT, JSON

class Chat(Base):
    __tablename__ = "chat"

    id = Column(String(36), primary_key=True)       # 会话id
    user_id = Column(String(36))                # 用户id
    title = Column(Text)                        # 会话标题
    chat = Column(JSON)                         # 会话记录

    created_at = Column(BigInteger)             # 创建时间
    updated_at = Column(BigInteger)             # 更新时间

    archived = Column(Boolean, default=False)                # 是否归档
    pinned = Column(Boolean, default=False, nullable=True)   # 是否置顶

    meta = Column(JSON)    # 存储与聊天相关的元数据，可包含标签、自定义属性、扩展信息等
    folder_id = Column(Text, nullable=True)     # 聊天所属文件夹的标识符




