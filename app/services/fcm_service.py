import os
import firebase_admin
from firebase_admin import credentials, messaging
from dotenv import load_dotenv
from app.models.device import Device

load_dotenv()

# 🔥 Initialize Firebase safely
firebase_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

if not firebase_path:
    raise Exception("FIREBASE_CREDENTIALS_PATH not set in .env")

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_path)
    firebase_admin.initialize_app(cred)


def send_fcm_to_user(db, user_id, title, body):

    devices = db.query(Device).filter(
        Device.user_id == user_id,
        Device.is_active == 1
    ).all()

    tokens = [d.fcm_token for d in devices]

    if not tokens:
        return {"message": "No active devices"}

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        tokens=tokens,
    )

    response = messaging.send_multicast(message)

    return {
        "success": response.success_count,
        "failure": response.failure_count
    }