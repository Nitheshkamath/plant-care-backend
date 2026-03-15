
from sqlalchemy import Column, Integer, String, DateTime
from app.database.db import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String(100), unique=True)
    password = Column(String(255))

    picture = Column(String)

    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)
    reset_otp = Column(String(10), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    


    plants = relationship("UserPlant", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")