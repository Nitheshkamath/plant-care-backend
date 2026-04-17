from sqlalchemy.orm import Session
from app.models.care_histroy import CareHistory
from app.models.user_plant import UserPlant
from datetime import timezone
import pytz

IST = pytz.timezone("Asia/Kolkata")

def get_user_care_history(db: Session, user_id: int):

    logs = (
        db.query(CareHistory, UserPlant)
        .join(UserPlant, CareHistory.plant_id == UserPlant.id)
        .filter(CareHistory.user_id == user_id)
        .order_by(CareHistory.created_at.desc())
        .all()
    )

    result = []

    for history, plant in logs:

        image = plant.plant_image

        if not image and plant.plant:
            image = plant.plant.image_url

        created_at = history.created_at

        # ✅ HANDLE OLD DATA (no timezone)
        if created_at.tzinfo is None:
            # assume stored in IST → convert properly to UTC
            created_at = IST.localize(created_at).astimezone(timezone.utc)

        else:
            # ensure it's UTC
            created_at = created_at.astimezone(timezone.utc)

        result.append({
            "id": history.id,
            "plant_id": history.plant_id,
            "plant_name": plant.plant_name,
            "plant_image": image,
            "action_type": history.action_type,
            "note": history.note,
            "created_at": created_at.isoformat()  # ✅ FINAL OUTPUT
        })

    return result

def clear_user_care_history(db: Session, user_id: int):

    logs = (
        db.query(CareHistory)
        .filter(CareHistory.user_id == user_id)
        .all()
    )

    if not logs:
        return {"message": "No history found"}

    for log in logs:
        db.delete(log)

    db.commit()

    return {"message": "Care history cleared successfully"}