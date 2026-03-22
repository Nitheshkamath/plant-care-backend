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

# 🔥 Initialize Firebase (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    print("🔥 Firebase initialized successfully")


def send_fcm_to_user(db, user_id, reminder):

    print(f"\n📤 Sending FCM for user {user_id} | Reminder {reminder.id}")

    devices = db.query(Device).filter(
        Device.user_id == user_id,
        Device.is_active == 1
    ).all()

    tokens = [d.fcm_token for d in devices if d.fcm_token]

    print("📱 Tokens found:", tokens)

    if not tokens:
        print("⚠️ No active devices")
        return {"message": "No active devices"}

    # 🌿 Plant name
    plant_name = "Your Plant"
    try:
        if reminder.plant:
            plant_name = reminder.plant.plant_name
    except Exception as e:
        print("⚠️ Plant fetch error:", e)

    # 🌿 Emoji
    emoji_map = {
        "watering": "💧",
        "fertilizing": "🌱",
        "trimming": "✂️",
        "repotting": "🪴",
        "sunlight_check": "☀️",
        "pest_inspection": "🐛",
    }

    emoji = emoji_map.get(reminder.title, "🌿")

    # 🔥 Notification
    title = f"{emoji} Time to take care of your plant"

    body = f"{reminder.title.capitalize()} your {plant_name}"

    if reminder.description:
        body += f"\n{reminder.description}"

    print("📝 Title:", title)
    print("📝 Body:", body)

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
            response = messaging.send(message)
            print(f"✅ Sent to {token}: {response}")

            results.append({
                "token": token,
                "status": "success"
            })

        except Exception as e:

            error_msg = str(e)
            print(f"❌ Error sending to {token}: {error_msg}")

            # 🔥 REMOVE INVALID TOKEN
            if "Requested entity was not found" in error_msg:
                print(f"🗑 Removing invalid token: {token}")

                device = db.query(Device).filter(
                    Device.fcm_token == token
                ).first()

                if device:
                    device.is_active = 0
                    db.commit()

            results.append({
                "token": token,
                "error": error_msg
            })

    return results