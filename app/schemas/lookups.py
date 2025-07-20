from datetime import datetime
from typing import Any
from pydantic import BaseModel


class LookupUpdate(BaseModel):
    items: Any


class LookupOut(BaseModel):
    name: str
    items: Any
    updated_at: datetime

    class Config:
        from_attributes = True

