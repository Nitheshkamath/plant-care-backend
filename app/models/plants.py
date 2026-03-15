from sqlalchemy import Column, Integer, String, Text
from app.database.db import Base

class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    botanical_name = Column(String(150))

    light = Column(String(100))
    humidity = Column(String(100))
    temperature = Column(String(100))

    water_requirement = Column(Text)
    propagation = Column(Text)
    maintenance = Column(Text)
    care = Column(Text)
    interesting_facts = Column(Text)
    category = Column(String)
    recommended_pot_size = Column(String(100))

    image_url = Column(Text)