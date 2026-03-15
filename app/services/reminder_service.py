from sqlalchemy.orm import Session
from datetime import datetime
import pytz

from app.models.reminder import Reminder
from app.models.care_histroy import CareHistory
from app.schemas.reminder_schema import ReminderCreate
from app.models.user_plant import UserPlant
from app.models.plants import Plant


# CREATE REMINDER
def create_reminder(db: Session, user, data: ReminderCreate):

    # ⭐ DUPLICATE CHECK
    existing = db.query(Reminder).filter(
        Reminder.user_id == user.id,
        Reminder.plant_id == data.plant_id,
        Reminder.type == data.type,
        Reminder.reminder_time == data.reminder_time,
        Reminder.status == "pending"
    ).first()

    if existing:
        return {"error": "Reminder already exists for this plant at the same time"}

    reminder = Reminder(
        user_id=user.id,
        plant_id=data.plant_id,
        title=data.title,
        description=data.description,
        reminder_time=data.reminder_time,
        type=data.type,
        day_of_week=data.day_of_week,
        status="pending",
        created_by=user.email
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return reminder


# GET USER REMINDERS
def get_user_reminders(db: Session, user_id: int):

    reminders = (
        db.query(Reminder, UserPlant)
        .join(UserPlant, Reminder.plant_id == UserPlant.id)
        .filter(Reminder.user_id == user_id)
        .order_by(Reminder.reminder_time.asc())
        .all()
    )

    result = []

    for reminder, plant in reminders:
        image = plant.plant_image

        if not image and plant.plant:
            image = plant.plant.image_url 


        result.append({
            "id": reminder.id,
            "plant_id": reminder.plant_id,
            "plant_name": plant.plant_name,
            "plant_image": image if image else None,
            "title": reminder.title,
            "description": reminder.description,
            "type": reminder.type,
            "day_of_week": reminder.day_of_week,
            "reminder_time": reminder.reminder_time,
            "created_at": reminder.created_at,
            "created_by": reminder.created_by
        })

    return result


# GET PENDING REMINDERS
def get_pending_reminders(db: Session, user_id: int):

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    return (
        db.query(Reminder)
        .filter(
            Reminder.user_id == user_id,
            Reminder.status == "pending",
            Reminder.reminder_time <= now
        )
        .order_by(Reminder.reminder_time.asc())
        .all()
    )


# COMPLETE REMINDER
def complete_reminder(db: Session, reminder_id: int, user_id: int):

    reminder = (
        db.query(Reminder)
        .filter(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id
        )
        .first()
    )

    if not reminder:
        return None

    reminder.status = "completed"

    history = CareHistory(
        user_id=user_id,
        plant_id=reminder.plant_id,
        action_type=reminder.type,
        note=reminder.title,
        created_at=datetime.utcnow()
    )

    db.add(history)

    db.commit()
    db.refresh(reminder)

    return reminder


# SKIP REMINDER
def skip_reminder(db: Session, reminder_id: int, user_id: int):

    reminder = (
        db.query(Reminder)
        .filter(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id
        )
        .first()
    )

    if not reminder:
        return None

    reminder.status = "skipped"

    db.commit()
    db.refresh(reminder)

    return reminder


# DELETE REMINDER
def delete_reminder(db: Session, reminder_id: int, user_id: int):

    reminder = (
        db.query(Reminder)
        .filter(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id
        )
        .first()
    )

    if reminder:
        db.delete(reminder)
        db.commit()

    return reminder


# UPDATE REMINDER
def update_reminder(db: Session, reminder_id: int, user_id: int, data):

    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == user_id
    ).first()

    if not reminder:
        return None

    # FINAL VALUES (use existing if not provided)
    plant_id = data.plant_id if data.plant_id is not None else reminder.plant_id
    reminder_type = data.type if data.type is not None else reminder.type
    reminder_time = data.reminder_time if data.reminder_time is not None else reminder.reminder_time

    # ⭐ DUPLICATE CHECK
    duplicate = db.query(Reminder).filter(
        Reminder.user_id == user_id,
        Reminder.plant_id == plant_id,
        Reminder.type == reminder_type,
        Reminder.reminder_time == reminder_time,
        Reminder.id != reminder_id
    ).first()

    if duplicate:
        return {"error": "Another reminder already exists with same plant and time"}

    # ⭐ CHECK IF ANY CHANGE
    if (
        plant_id == reminder.plant_id and
        (data.title is None or data.title == reminder.title) and
        (data.description is None or data.description == reminder.description) and
        reminder_time == reminder.reminder_time and
        reminder_type == reminder.type and
        (data.day_of_week is None or data.day_of_week == reminder.day_of_week)
    ):
        return {"error": "No record updated"}

    # UPDATE FIELDS
    reminder.plant_id = plant_id

    if data.title is not None:
        reminder.title = data.title

    if data.description is not None:
        reminder.description = data.description

    reminder.reminder_time = reminder_time
    reminder.type = reminder_type

    if data.day_of_week is not None:
        reminder.day_of_week = data.day_of_week


    db.commit()
    db.refresh(reminder)

    return reminder


# ALERT COUNT
def get_pending_alert_count(db: Session, user_id: int):

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    return (
        db.query(Reminder)
        .filter(
            Reminder.user_id == user_id,
            Reminder.status == "pending",
            Reminder.reminder_time <= now
        )
        .count()
    )


# COMPLETE ALL REMINDERS
def complete_all_reminders(db: Session, user_id: int):

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    reminders = (
        db.query(Reminder)
        .filter(
            Reminder.user_id == user_id,
            Reminder.status == "pending",
            Reminder.reminder_time <= now
        )
        .all()
    )

    for reminder in reminders:

        reminder.status = "completed"

        history = CareHistory(
            user_id=user_id,
            plant_id=reminder.plant_id,
            action_type=reminder.type,
            note=reminder.title,
            created_at=datetime.utcnow()
        )

        db.add(history)

    db.commit()

    return {"completed": len(reminders)}