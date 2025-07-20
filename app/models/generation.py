from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.db import Base

class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    template_version_id = Column(Integer, ForeignKey("template_versions.id"), nullable=False)
    params_json = Column(Text, nullable=True)
    status = Column(String, default="completed")
    result_path = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    version = relationship("TemplateVersion")
