from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.models.reminder import Reminder
from app.models.care_histroy import CareHistory
from app.schemas.reminder_schema import ReminderCreate
from app.models.user_plant import UserPlant


# 🔥 HELPER: calculate next trigger
def calculate_next_trigger(reminder_time, reminder_type, day_of_week=None):

    if reminder_type == "daily":
        return reminder_time + timedelta(days=1)

    elif reminder_type == "weekly" and day_of_week:
        days_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
        }

        today = reminder_time.weekday()
        target = days_map.get(day_of_week.lower(), today)

        delta = (target - today) % 7
        delta = 7 if delta == 0 else delta

        return reminder_time + timedelta(days=delta)

    return None


# CREATE REMINDER
def create_reminder(db: Session, user, data: ReminderCreate):

    reminder_time = data.reminder_time

    # ✅ Ensure UTC
    if reminder_time.tzinfo is None:
        reminder_time = reminder_time.replace(tzinfo=timezone.utc)
    else:
        reminder_time = reminder_time.astimezone(timezone.utc)

    # ⭐ DUPLICATE CHECK
    existing = db.query(Reminder).filter(
        Reminder.user_id == user.id,
        Reminder.plant_id == data.plant_id,
        Reminder.type == data.type,
        Reminder.reminder_time == reminder_time,
        Reminder.status == "pending"
    ).first()

    if existing:
        return {"error": "Reminder already exists"}

    reminder = Reminder(
        user_id=user.id,
        plant_id=data.plant_id,
        title=data.title,
        description=data.description,
        reminder_time=reminder_time,
        type=data.type,
        day_of_week=data.day_of_week,
        status="pending",
        is_active=True,
        next_trigger_time=reminder_time,  # 🔥 IMPORTANT
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
            "reminder_time": reminder.reminder_time.isoformat(),
            "next_trigger_time": reminder.next_trigger_time.isoformat() if reminder.next_trigger_time else None,
            "created_at": reminder.created_at.isoformat(),
            "created_by": reminder.created_by
        })

    return result


# 🔥 FCM / CRON: GET DUE REMINDERS (FIXED)
def get_due_reminders(db: Session):

    now = datetime.now(timezone.utc)
    print("⏰ DEBUG NOW UTC:", now)

    reminders = db.query(Reminder).filter(
        Reminder.is_active == True,
        Reminder.next_trigger_time <= now
    ).all()

    print("📦 DEBUG FOUND:", len(reminders))

    for r in reminders:
        print("➡️ DEBUG REMINDER:", r.id, r.next_trigger_time, r.status)

    return reminders


# 🔥 UPDATE AFTER TRIGGER
def mark_reminder_triggered(db: Session, reminder: Reminder):

    now = datetime.now(timezone.utc)

    reminder.last_triggered_at = now

    # 🔁 Calculate next trigger
    next_time = calculate_next_trigger(reminder.next_trigger_time,reminder.type,reminder.day_of_week)

    if next_time:
        reminder.next_trigger_time = next_time
    else:
        reminder.is_active = False

    db.commit()


# COMPLETE REMINDER
def complete_reminder(db: Session, reminder_id: int, user_id: int):

    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == user_id
    ).first()

    if not reminder:
        return None

    reminder.status = "completed"
    reminder.is_active = False

    history = CareHistory(
        user_id=user_id,
        plant_id=reminder.plant_id,
        action_type=reminder.type,
        note=reminder.title,
        created_at=datetime.now(timezone.utc)
    )

    db.add(history)
    db.commit()
    db.refresh(reminder)

    return reminder


# SKIP REMINDER
def skip_reminder(db: Session, reminder_id: int, user_id: int):

    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == user_id,
    ).first()

    if not reminder:
        return None

    reminder.status = "skipped"

    # 🔥 REMOVE FROM ALERTS
    reminder.last_triggered_at = None

    # 🔁 MOVE TO NEXT CYCLE
    next_time = calculate_next_trigger(
        reminder.next_trigger_time,
        reminder.type,
        reminder.day_of_week
    )

    if next_time:
        reminder.next_trigger_time = next_time
        reminder.is_active = True   # ensure still active
    else:
        reminder.is_active = False

    db.commit()
    db.refresh(reminder)

    return reminder

# DELETE REMINDER
def delete_reminder(db: Session, reminder_id: int, user_id: int):

    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == user_id
    ).first()

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

    # ✅ UTC FIX
    if data.reminder_time is not None:
        reminder_time = data.reminder_time

        if reminder_time.tzinfo is None:
            reminder_time = reminder_time.replace(tzinfo=timezone.utc)
        else:
            reminder_time = reminder_time.astimezone(timezone.utc)
    else:
        reminder_time = reminder.reminder_time

    # ⭐ DUPLICATE CHECK
    duplicate = db.query(Reminder).filter(
        Reminder.user_id == user_id,
        Reminder.plant_id == reminder.plant_id,
        Reminder.type == reminder.type,
        Reminder.reminder_time == reminder_time,
        Reminder.id != reminder_id
    ).first()

    if duplicate:
        return {"error": "Duplicate reminder exists"}

    reminder.reminder_time = reminder_time
    reminder.next_trigger_time = reminder_time  # 🔥 RESET

    if data.title is not None:
        reminder.title = data.title

    if data.description is not None:
        reminder.description = data.description

    if data.type is not None:
        reminder.type = data.type

    if data.day_of_week is not None:
        reminder.day_of_week = data.day_of_week

    db.commit()
    db.refresh(reminder)

    return reminder


# ALERT COUNT (FIXED)
def get_pending_alert_count(db: Session, user_id: int):

    return db.query(Reminder).filter(
        Reminder.user_id == user_id,
        Reminder.status == "pending",
        Reminder.last_triggered_at != None
    ).count()


# COMPLETE ALL
def complete_all_reminders(db: Session, user_id: int):

    now = datetime.now(timezone.utc)

    reminders = db.query(Reminder).filter(
        Reminder.user_id == user_id,
        Reminder.status == "pending",
        Reminder.last_triggered_at != None
    ).all()

    for reminder in reminders:

        reminder.status = "completed"
        reminder.is_active = False

        history = CareHistory(
            user_id=user_id,
            plant_id=reminder.plant_id,
            action_type=reminder.type,
            note=reminder.title,
            created_at=datetime.now(timezone.utc)
        )

        db.add(history)

    db.commit()

    return {"completed": len(reminders)}


def get_pending_reminders(db: Session, user_id: int):

    now = datetime.now(timezone.utc)

    reminders = db.query(Reminder).filter(
        Reminder.user_id == user_id,
        Reminder.status == "pending",
        Reminder.next_trigger_time <= now
    ).all()

    return reminders