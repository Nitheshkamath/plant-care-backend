from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReminderCreate(BaseModel):

    plant_id: int
    title: str
    description: Optional[str] = None
    reminder_time: datetime
    type: str
    day_of_week: Optional[str] = None


class ReminderResponse(BaseModel):

    id: int
    plant_id: int

    plant_name: Optional[str] = None
    plant_image: Optional[str] = None

    title: str
    description: Optional[str] = None

    reminder_time: datetime
    type: str
    day_of_week: Optional[str] = None

    status: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class ReminderUpdate(BaseModel):

    plant_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    reminder_time: Optional[datetime] = None
    type: Optional[str] = None
    day_of_week: Optional[str] = None

    class Config:
        from_attributes = True