from sqlalchemy.orm import Session
from app.models.user_plant import UserPlant


def create_user_plant(db: Session, user_id: int, data):

    plant = UserPlant(
        user_id=user_id,
        plant_name=data.plant_name,
        plant_type=data.plant_type,
        pot_size=data.pot_size,
        location=data.location,
        watering_schedule=data.watering_schedule
    )

    db.add(plant)
    db.commit()
    db.refresh(plant)

    return plant


def get_user_plants(db: Session, user_id: int):

    return db.query(UserPlant).filter(
        UserPlant.user_id == user_id
    ).all()