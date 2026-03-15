from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database.db import SessionLocal
from app.services.care_histroy_service import get_user_care_history,clear_user_care_history
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/care-history",
    tags=["Care History"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):


    return get_user_care_history(db, current_user.id)


@router.delete("/")
def clear_care_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return clear_user_care_history(db, current_user.id)