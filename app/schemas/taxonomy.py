from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel


class TaxonomyNodeBase(BaseModel):
    parent_id: Optional[int] = None
    slug: str
    title: str
    order: Optional[int] = 0


class TaxonomyNodeCreate(TaxonomyNodeBase):
    pass


class TaxonomyNodeUpdate(BaseModel):
    parent_id: Optional[int] = None
    slug: Optional[str] = None
    title: Optional[str] = None
    order: Optional[int] = None


class TaxonomyNodeOut(TaxonomyNodeBase):
    id: int
    children: List['TaxonomyNodeOut'] = []

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

