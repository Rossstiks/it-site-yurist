from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.db import SessionLocal
from app.models import Template
from app.schemas.templates import TemplateOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/templates", response_model=List[TemplateOut])
def search_templates(q: str, db: Session = Depends(get_db)):
    query = db.query(Template).filter(
        or_(Template.title.ilike(f"%{q}%"), Template.code.ilike(f"%{q}%"))
    )
    return query.all()
