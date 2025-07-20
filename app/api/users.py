from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserCreate, UserOut
from app.api.auth import require_roles, get_db
from app.core.security import get_password_hash

router = APIRouter()


def list_users(db: Session):
    return db.query(User).all()


@router.get("/", response_model=list[UserOut])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return list_users(db)


@router.post("/", response_model=UserOut, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

