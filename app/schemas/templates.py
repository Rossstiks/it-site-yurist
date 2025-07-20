from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TemplateBase(BaseModel):
    taxonomy_id: Optional[int] = None
    code: str
    title: str

class TemplateCreate(TemplateBase):
    jinja_body: str
    version: str = "1.0.0"
    changelog: Optional[str] = None

class TemplateVersionOut(BaseModel):
    id: int
    version: str
    jinja_body: str
    changelog: Optional[str]
    created_at: datetime
    is_latest: bool

    class Config:
        orm_mode = True

class TemplateOut(BaseModel):
    id: int
    taxonomy_id: Optional[int]
    code: str
    title: str
    created_at: datetime
    versions: list[TemplateVersionOut] = []

    class Config:
        orm_mode = True
