from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.models.plants import Plant

router = APIRouter()

# -----------------------------
# DATABASE DEPENDENCY
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# HELPER FUNCTION (serialize)
# -----------------------------
def plant_to_dict(p: Plant):
    return {
        "id": p.id,
        "name": p.name,
        "botanical_name": p.botanical_name,
        "light": p.light,
        "humidity": p.humidity,
        "temperature": p.temperature,
        "water_requirement": p.water_requirement,
        "propagation": p.propagation,
        "maintenance": p.maintenance,
        "care": p.care,
        "interesting_facts": p.interesting_facts,
        "image_url": p.image_url,
        "category": p.category,
        "recommended_pot_size": p.recommended_pot_size  
    }


# -----------------------------
# GET ALL PLANTS
# -----------------------------
@router.get("/plants")
def get_all_plants(db: Session = Depends(get_db)):

    plants = db.query(Plant).all()

    return {
        "count": len(plants),
        "plants": [plant_to_dict(p) for p in plants]
    }


# -----------------------------
# GET SINGLE PLANT
# -----------------------------
@router.get("/plants/{plant_id}")
def get_plant_details(plant_id: int, db: Session = Depends(get_db)):

    plant = db.query(Plant).filter(Plant.id == plant_id).first()

    if not plant:
        raise HTTPException(
            status_code=404,
            detail="Plant not found"
        )

    return plant_to_dict(plant)


# -----------------------------
# SEARCH PLANTS
# -----------------------------
@router.get("/plants/search/{name}")
def search_plants(name: str, db: Session = Depends(get_db)):

    plants = db.query(Plant).filter(
        Plant.name.ilike(f"%{name}%")
    ).all()

    return [plant_to_dict(p) for p in plants]