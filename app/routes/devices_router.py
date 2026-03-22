from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone

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


# 🔥 REQUEST BODY
class DeviceRegister(BaseModel):
    fcm_token: str
    device_type: str = "android"


# 🔥 REGISTER DEVICE API (FINAL VERSION)
@router.post("/register")
def register_device(
    data: DeviceRegister,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    token = data.fcm_token.strip()

    print(f"📱 Registering device for user {user.id}")
    print(f"🔑 Token: {token}")

    # 🔍 Check if token already exists
    existing_token = db.query(Device).filter(
        Device.fcm_token == token
    ).first()

    if existing_token:
        # 🔁 Reassign token safely
        existing_token.user_id = user.id
        existing_token.is_active = True
        existing_token.device_type = data.device_type
        existing_token.updated_at = datetime.now(timezone.utc)

        print("♻️ Existing token updated")

    else:
        # ❌ OPTIONAL: deactivate old devices of same user
        db.query(Device).filter(
            Device.user_id == user.id
        ).update({
            "is_active": False
        })

        # ✅ Add new device
        new_device = Device(
            user_id=user.id,
            fcm_token=token,
            device_type=data.device_type,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        db.add(new_device)

        print("✅ New device added")

    db.commit()

    return {
        "message": "Device registered successfully",
        "user_id": user.id
    }