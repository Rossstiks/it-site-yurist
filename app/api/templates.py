from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models import Template, TemplateVersion, User
from app.api.auth import require_roles
from app.core.audit import log_action
from app.schemas.templates import TemplateCreate, TemplateOut, TemplateVersionOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[TemplateOut])
def list_templates(db: Session = Depends(get_db)):
    return db.query(Template).all()


@router.get("/{template_id}", response_model=TemplateOut)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/", response_model=TemplateOut, status_code=201)
def create_template(
    payload: TemplateCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("editor", "admin")),
):
    template = Template(
        code=payload.code,
        title=payload.title,
        taxonomy_id=payload.taxonomy_id,
    )
    db.add(template)
    db.flush()  # to assign id
    version = TemplateVersion(
        template_id=template.id,
        version=payload.version,
        jinja_body=payload.jinja_body,
        changelog=payload.changelog,
        is_latest=True,
    )
    template.versions.append(version)
    db.add(version)
    db.commit()
    log_action(db, "template", template.id, "create", None)
    db.refresh(template)
    return template
