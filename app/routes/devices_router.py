from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.device import Device
from app.core.security import get_current_user
from app.database.db import SessionLocal

router = APIRouter(prefix="/devices", tags=["Devices"])


# 🔥 DB DEPENDENCY
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔥 REQUEST BODY (IMPORTANT FIX)
class DeviceRegister(BaseModel):
    fcm_token: str
    device_type: str = "android"


# 🔥 REGISTER DEVICE API (FIXED)
@router.post("/register")
def register_device(
    data: DeviceRegister,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    token = data.fcm_token

    # 🔍 Check if token already exists
    existing = db.query(Device).filter(
        Device.fcm_token == token
    ).first()

    if existing:
        existing.user_id = user.id
        existing.is_active = 1
        existing.device_type = data.device_type
    else:
        device = Device(
            user_id=user.id,
            fcm_token=token,
            device_type=data.device_type,
            is_active=1
        )
        db.add(device)

    db.commit()

    return {
        "message": "Device registered successfully",
        "fcm_token": token
    }