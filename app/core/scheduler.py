from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.services.reminder_service import get_due_reminders, mark_reminder_triggered
from app.services.fcm_service import send_fcm_to_user


def run_scheduler():

    scheduler = BackgroundScheduler()

    def job():
        db: Session = SessionLocal()

        try:
            reminders = get_due_reminders(db)

            for r in reminders:
                send_fcm_to_user(db, r.user_id, r.title, r.description)
                mark_reminder_triggered(db, r)

        finally:
            db.close()

    scheduler.add_job(job, 'interval', minutes=1)
    scheduler.start()