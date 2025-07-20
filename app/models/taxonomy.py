from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.db import Base


class TaxonomyNode(Base):
    __tablename__ = "taxonomy_nodes"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("taxonomy_nodes.id"), nullable=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    order = Column(Integer, default=0)

    parent = relationship("TaxonomyNode", remote_side=[id], backref="children")
    templates = relationship("Template", back_populates="taxonomy")
