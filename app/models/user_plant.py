from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class UserPlant(Base):

    __tablename__ = "user_plants"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    plant_library_id = Column(Integer, ForeignKey("plants.id"))

    plant_name = Column(String(100))
    plant_type = Column(String(100))

    pot_size = Column(String(50))
    location = Column(String(200))
    watering_schedule = Column(String(200))

    plant_image = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    reminders = relationship("Reminder",back_populates="plant")
    care_history = relationship("CareHistory", back_populates="plant",cascade="all, delete")
    plant = relationship("Plant") 