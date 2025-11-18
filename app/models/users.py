import time
from typing import Optional
from app.database.db import Base
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT, JSON

class User(Base):
    __tablename__ = "user"
    id = Column(String(36), primary_key=True)
    name = Column(String(50))
    email = Column(String(50))
    role = Column(String(50))
    profile_image_url = Column(Text)

    last_active_at = Column(BigInteger)
    updated_at = Column(BigInteger)
    created_at = Column(BigInteger)

    api_key = Column(String, nullable=True, unique=True)
    settings = Column(JSON, nullable=True)
    info = Column(JSON, nullable=True)

    oauth_sub = Column(Text, unique=True)