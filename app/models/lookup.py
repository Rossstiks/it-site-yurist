from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

from app.core.db import Base


class Lookup(Base):
    __tablename__ = "lookups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    items_json = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

