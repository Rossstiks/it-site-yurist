from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FieldBase(BaseModel):
    template_id: int
    name: str
    label: str
    type: str
    required: bool = False
    config_json: Optional[str] = None
    order: int = 0


class FieldCreate(FieldBase):
    pass


class FieldOut(FieldBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
