from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.core.db import Base


class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    name = Column(String, nullable=False)
    label = Column(String, nullable=False)
    type = Column(String, nullable=False)
    required = Column(Boolean, default=False)
    config_json = Column(Text, nullable=True)
    order = Column(Integer, default=0)

    template = relationship("Template", back_populates="fields")
