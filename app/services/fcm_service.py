import os
import json
import firebase_admin
from firebase_admin import credentials, messaging
from app.models.device import Device
from app.services.reminder_service import get_pending_alert_count


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


def send_fcm_to_user(db, user_id, reminder):

    devices = db.query(Device).filter(
        Device.user_id == user_id,
        Device.is_active == 1
    ).all()

    tokens = [d.fcm_token for d in devices if d.fcm_token]

    if not tokens:
        return {"message": "No active devices"}

    # 🔥 Get plant name safely
    plant_name = "Your Plant"
    if reminder.plant:
        plant_name = reminder.plant.plant_name

    # 🔥 Emoji mapping
    emoji_map = {
        "watering": "💧",
        "fertilizing": "🌱",
        "trimming": "✂️",
        "repotting": "🪴",
        "sunlight_check": "☀️",
        "pest_inspection": "🐛",
    }

    emoji = emoji_map.get(reminder.title, "🌿")

    # 🔥 Notification content
    title = f"{emoji} Time to take care of your plant"
    
    body = (
        reminder.description
        if reminder.description
        else f"{reminder.title.capitalize()} - {plant_name}"
    )

    # 🔥 Badge count
    badge_count = get_pending_alert_count(db, user_id)

    results = []

    for token in tokens:

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={
                "badge": str(badge_count),
                "type": "reminder",
                "plant_name": plant_name,
                "action": reminder.title
            },
            token=token,
        )

        try:
            messaging.send(message)
            results.append({"token": token, "status": "success"})
        except Exception as e:
            results.append({"token": token, "error": str(e)})

    return results