from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.db import Base

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    taxonomy_id = Column(Integer, ForeignKey("taxonomy_nodes.id"), nullable=True)
    code = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    taxonomy = relationship("TaxonomyNode", back_populates="templates")
    versions = relationship(
        "TemplateVersion",
        back_populates="template",
        cascade="all, delete-orphan",
    )
    fields = relationship(
        "Field",
        back_populates="template",
        cascade="all, delete-orphan",
    )


class TemplateVersion(Base):
    __tablename__ = "template_versions"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    version = Column(String, nullable=False)
    jinja_body = Column(Text, nullable=False)
    changelog = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_latest = Column(Boolean, default=False)

    template = relationship("Template", back_populates="versions")
