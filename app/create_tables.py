from app.database.db import engine, Base

# 🔥 import ALL models (this registers them)
from app.models.user import User
from app.models.reminder import Reminder
from app.models.care_histroy import CareHistory
from app.models.user_plant import UserPlant
from app.models.device import Device
from app.models.plants import Plant



def create_tables():
    print("Creating all tables in Supabase...")
    Base.metadata.create_all(bind=engine)
    print("Done ✅")


if __name__ == "__main__":
    create_tables()