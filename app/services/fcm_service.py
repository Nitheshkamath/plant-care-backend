import os
import json
import firebase_admin
from firebase_admin import credentials, messaging
from app.models.device import Device


# 🔥 Load Firebase JSON from ENV
firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

if not firebase_json:
    raise Exception("FIREBASE_CREDENTIALS_JSON not set")

# 🔥 Convert JSON string → dict
cred_dict = json.loads(firebase_json)

# 🔥 Initialize Firebase safely (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)


def send_fcm_to_user(db, user_id, title, body):

    devices = db.query(Device).filter(
        Device.user_id == user_id,
        Device.is_active == 1
    ).all()

    tokens = [d.fcm_token for d in devices if d.fcm_token]

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