from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class CareHistory(Base):

    __tablename__ = "care_history"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    plant_id = Column(Integer, ForeignKey("user_plants.id"), nullable=False)

    action_type = Column(String(50), nullable=False)
    # watered / fertilized / repotted / trimmed / note

    note = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    user = relationship("User")
    plant = relationship("UserPlant", back_populates="care_history")