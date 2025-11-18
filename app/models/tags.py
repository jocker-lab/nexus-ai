from sqlalchemy import Column, String, PrimaryKeyConstraint
from app.database.db import Base
from sqlalchemy.dialects.mysql import MEDIUMTEXT, JSON


class Tag(Base):
    __tablename__ = "tag"
    id = Column(String(36))
    name = Column(String(50))
    user_id = Column(String(36))
    meta = Column(JSON, nullable=True)

    # Unique constraint ensuring (id, user_id) is unique, not just the `id` column
    __table_args__ = (PrimaryKeyConstraint("id", "user_id", name="pk_id_user_id"),)


