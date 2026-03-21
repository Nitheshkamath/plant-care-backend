from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.db import SessionLocal
from app.schemas.reminder_schema import ReminderCreate, ReminderResponse,ReminderUpdate
from app.services.reminder_service import (
    create_reminder,
    get_user_reminders,
    delete_reminder,
    update_reminder,
    skip_reminder,
    complete_reminder,
    get_pending_alert_count,
    complete_all_reminders
)
from app.core.security import get_current_user
from app.models.user import User



router = APIRouter(
    prefix="/reminders",
    tags=["Reminders"]
)


# DB dependency
def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# CREATE REMINDER
@router.post("/", response_model=ReminderResponse)
def add_reminder(

    reminder: ReminderCreate,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    return create_reminder(db, current_user, reminder)


# GET USER REMINDERS
@router.get("/", response_model=List[ReminderResponse])
def list_reminders(

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    return get_user_reminders(db, current_user.id)


# DELETE REMINDER
@router.delete("/{reminder_id}")
def remove_reminder(

    reminder_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    reminder = delete_reminder(db, reminder_id, current_user.id)

    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    return {"message": "Reminder deleted successfully"}

# UPDATE REMINDER
@router.put("/{reminder_id}", response_model=ReminderResponse)
def edit_reminder(

    reminder_id: int,

    reminder: ReminderUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):

    updated = update_reminder(db, reminder_id, current_user.id, reminder)

    if not updated:
        raise HTTPException(status_code=404, detail="Reminder not found")

    return updated

@router.get("/pending")
def pending_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_pending_reminders(db, current_user.id)


@router.put("/{reminder_id}/complete")
def complete_reminder_api(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return complete_reminder(db, reminder_id, current_user.id)


@router.put("/{reminder_id}/skip")
def skip_reminder_api(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return skip_reminder(db, reminder_id, current_user.id)

@router.get("/alerts/count")
def alerts_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "count": get_pending_alert_count(db, current_user.id)
    }

@router.put("/complete-all")
def complete_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return complete_all_reminders(db, current_user.id)