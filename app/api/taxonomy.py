from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models import TaxonomyNode
from app.schemas.taxonomy import (
    TaxonomyNodeCreate,
    TaxonomyNodeUpdate,
    TaxonomyNodeOut,
)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TaxonomyNodeOut, status_code=201)
def create_node(payload: TaxonomyNodeCreate, db: Session = Depends(get_db)):
    node = TaxonomyNode(
        parent_id=payload.parent_id,
        slug=payload.slug,
        title=payload.title,
        order=payload.order or 0,
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def build_tree(nodes: List[TaxonomyNode], parent_id: Optional[int] = None) -> List[TaxonomyNodeOut]:
    children = [n for n in nodes if n.parent_id == parent_id]
    return [
        TaxonomyNodeOut(
            id=child.id,
            parent_id=child.parent_id,
            slug=child.slug,
            title=child.title,
            order=child.order,
            children=build_tree(nodes, child.id),
        )
        for child in children
    ]


@router.get("/tree", response_model=List[TaxonomyNodeOut])
def get_tree(db: Session = Depends(get_db)):
    nodes = db.query(TaxonomyNode).order_by(TaxonomyNode.order).all()
    return build_tree(nodes)


@router.put("/{node_id}", response_model=TaxonomyNodeOut)
def update_node(
    node_id: int, payload: TaxonomyNodeUpdate, db: Session = Depends(get_db)
):
    node = db.query(TaxonomyNode).filter(TaxonomyNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    if payload.parent_id is not None:
        node.parent_id = payload.parent_id
    if payload.slug is not None:
        node.slug = payload.slug
    if payload.title is not None:
        node.title = payload.title
    if payload.order is not None:
        node.order = payload.order
    db.commit()
    db.refresh(node)
    return node


@router.delete("/{node_id}", status_code=204)
def delete_node(node_id: int, db: Session = Depends(get_db)):
    node = db.query(TaxonomyNode).filter(TaxonomyNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    db.delete(node)
    db.commit()
    return None
