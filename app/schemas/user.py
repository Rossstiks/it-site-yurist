from datetime import datetime
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "viewer"

class UserOut(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
