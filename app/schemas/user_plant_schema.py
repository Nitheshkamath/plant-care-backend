from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserPlantCreate(BaseModel):
    plant_name: str
    plant_type: str
    pot_size: str
    location: str
    watering_schedule: str


class UserPlantResponse(BaseModel):

    id: int
    plant_name: str
    plant_type: Optional[str] = None
    pot_size: Optional[str] = None
    location: Optional[str] = None
    watering_schedule: Optional[str] = None
    plant_image: Optional[str] = None
    

    model_config = ConfigDict(from_attributes=True)