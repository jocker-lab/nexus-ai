from app.database.db import Base
from sqlalchemy import BigInteger, Boolean, Column, String, Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT, JSON

class File(Base):
    __tablename__ = "files"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36))
    hash = Column(Text, nullable=True)

    filename = Column(Text)
    path = Column(Text, nullable=True)

    data = Column(JSON, nullable=True)
    meta = Column(JSON, nullable=True)

    access_control = Column(JSON, nullable=True)

    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)

