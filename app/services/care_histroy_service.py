from sqlalchemy.orm import Session
from app.models.care_histroy import CareHistory
from app.models.user_plant import UserPlant


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

        # If no uploaded image → use library image
        if not image and plant.plant:
            image = plant.plant.image_url

        result.append({
            "id": history.id,
            "plant_id": history.plant_id,
            "plant_name": plant.plant_name,
            "plant_image": image,
            "action_type": history.action_type,
            "note": history.note,
            "created_at": history.created_at.isoformat()
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