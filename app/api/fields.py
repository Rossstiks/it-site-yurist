from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models import Field, User
from app.api.auth import require_roles
from app.schemas.fields import FieldCreate, FieldOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/bulk", response_model=List[FieldOut], status_code=201)
def create_fields(
    payload: List[FieldCreate],
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("editor", "admin")),
):
    fields = [Field(**item.dict()) for item in payload]
    db.add_all(fields)
    db.commit()
    for f in fields:
        db.refresh(f)
    return fields


@router.get("/", response_model=List[FieldOut])
def list_fields(template_id: int, db: Session = Depends(get_db)):
    return db.query(Field).filter(Field.template_id == template_id).order_by(Field.order).all()
