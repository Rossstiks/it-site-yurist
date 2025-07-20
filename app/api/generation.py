from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jinja2 import Template as JinjaTemplate

from app.core.db import SessionLocal
from app.models import Template, TemplateVersion
from app.schemas.generation import GenerateRequest, GenerateResponse

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=GenerateResponse)
def generate_document(payload: GenerateRequest, db: Session = Depends(get_db)):
    template = None
    if payload.template_id is not None:
        template = db.query(Template).filter(Template.id == payload.template_id).first()
    elif payload.code is not None:
        template = db.query(Template).filter(Template.code == payload.code).first()
    else:
        raise HTTPException(status_code=400, detail="template_id or code required")

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    version = (
        db.query(TemplateVersion)
        .filter(TemplateVersion.template_id == template.id, TemplateVersion.is_latest == True)
        .first()
    )
    if not version:
        raise HTTPException(status_code=404, detail="Template version not found")

    jinja = JinjaTemplate(version.jinja_body)
    result = jinja.render(**(payload.params or {}))
    return GenerateResponse(result=result)
