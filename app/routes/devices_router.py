from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.device import Device
from app.core.security import get_current_user 
from app.database.db import SessionLocal

router = APIRouter(prefix="/devices", tags=["Devices"])

def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register_device(token: str, db: Session = Depends(get_db), user=Depends(get_current_user)):

    existing = db.query(Device).filter(
        Device.fcm_token == token
    ).first()

    if existing:
        existing.user_id = user.id
        existing.is_active = 1
    else:
        device = Device(
            user_id=user.id,
            fcm_token=token,
            device_type="android"
        )
        db.add(device)

    db.commit()

    return {"message": "Device registered successfully"}