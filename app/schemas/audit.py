from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    action: str
    diff_json: Optional[str] = None
    actor_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True
