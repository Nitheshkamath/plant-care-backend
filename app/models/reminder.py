from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.db import Base


class Reminder(Base):

    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    plant_id = Column(
        Integer,
        ForeignKey("user_plants.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(String(200), nullable=False)

    description = Column(String(500), nullable=True)

    # timezone aware
    reminder_time = Column(DateTime(timezone=True), nullable=False, index=True)

    type = Column(String(50), nullable=False)  # daily / weekly / once

    day_of_week = Column(String(20), nullable=True)

    status = Column(String(20), default="pending", index=True)

    is_active = Column(Boolean, default=True)

    # 🔥 NEW FIELDS (IMPORTANT)

    last_triggered_at = Column(DateTime(timezone=True), nullable=True)

    next_trigger_time = Column(DateTime(timezone=True), nullable=True)

    is_synced = Column(Boolean, default=False)  # for mobile sync

    is_sent_fcm = Column(Boolean, default=False)  # fallback tracking

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    created_by = Column(String(100))
    is_alert_active = Column(Boolean, default=False, index=True)

    # relationships
    user = relationship("User")
    plant = relationship("UserPlant", back_populates="reminders")