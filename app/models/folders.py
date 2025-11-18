from app.database.db import Base
from sqlalchemy import BigInteger, Boolean, Column, Text, String
from sqlalchemy.dialects.mysql import MEDIUMTEXT, JSON



class Folder(Base):
    __tablename__ = "folder"
    # 基本字段
    id = Column(String(36), primary_key=True)             # 文件夹的唯一标识符
    user_id = Column(String(36))                          # 所属用户的ID
    parent_id = Column(String(36), nullable=True)         # 父文件夹的ID，用于构建文件夹层级结构
    name = Column(Text)                             # 文件夹名称

    # 扩展信息
    items = Column(JSON, nullable=True)             # 存储文件夹中的内容，包括聊天记录等
    meta = Column(JSON, nullable=True)              # 存储文件夹的额外信息，如标签、描述等
    is_expanded = Column(Boolean, default=False)    # 控制文件夹在前端是否展开显示

    # 时间信息
    created_at = Column(BigInteger)                 # 创建时间
    updated_at = Column(BigInteger)                 # 最后更新时间

