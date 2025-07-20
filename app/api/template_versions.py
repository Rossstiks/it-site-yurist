from typing import List, Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jinja2 import Template as JinjaTemplate

from app.core.db import SessionLocal
from app.models import Template, TemplateVersion, User
from app.api.auth import require_roles
from app.core.audit import log_action
from app.schemas.templates import TemplateVersionOut
from app.schemas.generation import GenerateResponse
from pydantic import BaseModel

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TemplateVersionCreate(BaseModel):
    version: str
    jinja_body: str
    changelog: Optional[str] = None
    is_latest: bool = False


class PreviewRequest(BaseModel):
    params: Optional[Dict[str, Any]] = None


@router.get("/templates/{template_id}/versions", response_model=List[TemplateVersionOut])
def list_versions(template_id: int, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return (
        db.query(TemplateVersion)
        .filter(TemplateVersion.template_id == template_id)
        .order_by(TemplateVersion.created_at)
        .all()
    )


@router.post(
    "/templates/{template_id}/versions",
    response_model=TemplateVersionOut,
    status_code=201,
)
def create_version(
    template_id: int,
    payload: TemplateVersionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("editor", "admin")),
):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if payload.is_latest:
        db.query(TemplateVersion).filter(
            TemplateVersion.template_id == template_id
        ).update({TemplateVersion.is_latest: False})
    version = TemplateVersion(
        template_id=template_id,
        version=payload.version,
        jinja_body=payload.jinja_body,
        changelog=payload.changelog,
        is_latest=payload.is_latest,
    )
    db.add(version)
    db.commit()
    log_action(db, "template_version", version.id, "create", None)
    db.refresh(version)
    return version


@router.get("/template-versions/{version_id}", response_model=TemplateVersionOut)
def get_version(version_id: int, db: Session = Depends(get_db)):
    version = db.query(TemplateVersion).filter(TemplateVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Template version not found")
    return version


@router.post(
    "/template-versions/{version_id}/preview",
    response_model=GenerateResponse,
)
def preview_version(
    version_id: int, payload: PreviewRequest, db: Session = Depends(get_db)
):
    version = db.query(TemplateVersion).filter(TemplateVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Template version not found")
    jinja = JinjaTemplate(version.jinja_body)
    result = jinja.render(**(payload.params or {}))
    return GenerateResponse(result=result)


@router.post(
    "/template-versions/{version_id}/publish",
    response_model=TemplateVersionOut,
)
def publish_version(
    version_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("editor", "admin"))
):
    version = db.query(TemplateVersion).filter(TemplateVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Template version not found")
    db.query(TemplateVersion).filter(TemplateVersion.template_id == version.template_id).update(
        {TemplateVersion.is_latest: False}
    )
    version.is_latest = True
    db.commit()
    log_action(db, "template_version", version.id, "publish", None)
    db.refresh(version)
    return version
