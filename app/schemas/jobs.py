from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class GenerationJobOut(BaseModel):
    id: int
    template_version_id: int
    status: str
    result_path: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True
