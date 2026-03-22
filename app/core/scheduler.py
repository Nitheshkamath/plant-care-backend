from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database.db import SessionLocal
from app.services.reminder_service import get_due_reminders, mark_reminder_triggered
from app.services.fcm_service import send_fcm_to_user


def run_scheduler():

    scheduler = BackgroundScheduler()

    def job():
        print("\n🔥 SCHEDULER RUNNING ------------------------")

        db: Session = SessionLocal()

        try:
            now = datetime.now(timezone.utc)
            print("⏰ NOW UTC:", now)

            reminders = get_due_reminders(db)

            print(f"📦 TOTAL DUE REMINDERS: {len(reminders)}")

            for r in reminders:
                print(f"➡️ Triggering Reminder ID: {r.id}")
                print(f"   👤 User ID: {r.user_id}")
                print(f"   🕒 Reminder Time (UTC): {r.reminder_time}")

                try:
                    # 🔔 SEND FCM
                    res = send_fcm_to_user(
                        db,
                        r.user_id,
                        r.title,
                        r.description
                    )

                    print("📲 FCM RESPONSE:", res)

                    # ✅ ONLY MARK IF SUCCESS
                    if isinstance(res, list) and any(
                        item.get("status") == "success" for item in res
                    ):
                        mark_reminder_triggered(db, r)
                        print(f"✅ Reminder {r.id} marked as triggered")
                    else:
                        print(f"⚠️ Reminder {r.id} NOT marked (FCM failed)")

                except Exception as e:
                    print(f"❌ FCM ERROR for reminder {r.id}:", str(e))

        except Exception as e:
            print("❌ JOB ERROR:", str(e))

        finally:
            db.close()
            print("🔒 DB SESSION CLOSED")

    # ⏱️ Run every 1 minute
    scheduler.add_job(job, 'interval', minutes=1)

    print("🚀 Scheduler started...")
    scheduler.start()