from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CareHistoryCreate(BaseModel):

    plant_id: int
    action_type: str
    note: Optional[str] = None


class CareHistoryResponse(BaseModel):

    id: int
    plant_id: int
    action_type: str
    note: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True