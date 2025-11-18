
from app.database.db import Base
from sqlalchemy import BigInteger, Boolean, Column, Text, String
from sqlalchemy.dialects.mysql import MEDIUMTEXT, JSON



class Model(Base):
    __tablename__ = "model"

    id = Column(Text, primary_key=True)
    user_id = Column(Text)
    base_model_id = Column(Text, nullable=True)
    name = Column(Text)
    params = Column(JSON)
    meta = Column(JSON)

    access_control = Column(JSON, nullable=True)  # Controls data access levels.

    is_active = Column(Boolean, default=True)

    updated_at = Column(BigInteger)
    created_at = Column(BigInteger)