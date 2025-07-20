import json
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jinja2 import Template as JinjaTemplate

from app.core.db import SessionLocal
from app.models import Template, TemplateVersion, GenerationJob
from app.schemas.generation import GenerateRequest
from app.schemas.jobs import GenerationJobOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=GenerationJobOut, status_code=201)
def create_generation_job(payload: GenerateRequest, db: Session = Depends(get_db)):
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

    os.makedirs("generated", exist_ok=True)
    path = os.path.join("generated", f"job_{int(datetime.utcnow().timestamp() * 1000)}.html")
    with open(path, "w") as fh:
        fh.write(result)

    job = GenerationJob(
        template_version_id=version.id,
        params_json=json.dumps(payload.params or {}),
        status="completed",
        result_path=path,
        finished_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/{job_id}", response_model=GenerationJobOut)
def read_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
