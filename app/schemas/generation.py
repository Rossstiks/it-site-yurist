from typing import Any, Dict, Optional
from pydantic import BaseModel


class GenerateRequest(BaseModel):
    template_id: Optional[int] = None
    code: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    format: str = "html"


class GenerateResponse(BaseModel):
    result: str
