from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class Reminder(Base):

    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    plant_id = Column(Integer,ForeignKey("user_plants.id", ondelete="CASCADE"),nullable=False)

    title = Column(String(200), nullable=False)

    description = Column(String(500), nullable=True)

    reminder_time = Column(DateTime, nullable=False)

    type = Column(String(50), nullable=False)  
    # daily / weekly

    day_of_week = Column(String(20), nullable=True)

    status = Column(String(50), default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)

    created_by = Column(String(100))  # storing users.email

    # relationships
    user = relationship("User")
    plant = relationship("UserPlant",back_populates="reminders")