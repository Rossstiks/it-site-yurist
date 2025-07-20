import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.db import SessionLocal
from app.models import Lookup
from app.schemas.lookups import LookupUpdate, LookupOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{name}", response_model=LookupOut, status_code=201)
def upsert_lookup(name: str, payload: LookupUpdate, db: Session = Depends(get_db)):
    lookup = db.query(Lookup).filter(Lookup.name == name).first()
    items_json = json.dumps(payload.items)
    if lookup:
        lookup.items_json = items_json
        lookup.updated_at = datetime.utcnow()
    else:
        lookup = Lookup(name=name, items_json=items_json)
        db.add(lookup)
    db.commit()
    db.refresh(lookup)
    lookup_dict = json.loads(lookup.items_json)
    return LookupOut(name=lookup.name, items=lookup_dict, updated_at=lookup.updated_at)


@router.get("/{name}", response_model=LookupOut)
def get_lookup(name: str, db: Session = Depends(get_db)):
    lookup = db.query(Lookup).filter(Lookup.name == name).first()
    if not lookup:
        raise HTTPException(status_code=404, detail="Lookup not found")
    return LookupOut(
        name=lookup.name,
        items=json.loads(lookup.items_json),
        updated_at=lookup.updated_at,
    )

