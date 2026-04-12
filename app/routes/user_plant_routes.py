from typing import Generator, List

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

import cloudinary.uploader 

from app.database.db import SessionLocal
from app.models.user_plant import UserPlant
from app.models.plants import Plant
from app.schemas.user_plant_schema import UserPlantResponse
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/my-plants",
    tags=["My Plants"]
)

# DATABASE DEPENDENCY
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🌱 ADD PLANT
@router.post("/", response_model=UserPlantResponse)
async def add_my_plant(

    plant_name: str = Form(...),
    plant_type: str = Form(None),
    pot_size: str = Form(None),
    location: str = Form(None),
    watering_schedule: str = Form(None),

    plant_image: UploadFile = File(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)

):

    # ⭐ DUPLICATE CHECK
    existing = db.query(UserPlant).filter(
        UserPlant.user_id == current_user.id,
        UserPlant.plant_name == plant_name,
        UserPlant.location == location
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Plant already exists in your garden"
        )

    image_path = None

    # ✅ CLOUDINARY UPLOAD
    if plant_image:
        print("NEW CODE RUNNING")
        print("CONTENT TYPE:", plant_image.content_type)

        if not plant_image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type")

        try:
            result = cloudinary.uploader.upload(plant_image.file)
            image_path = result["secure_url"]

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    new_plant = UserPlant(
        user_id=current_user.id,
        plant_name=plant_name,
        plant_type=plant_type,
        pot_size=pot_size,
        location=location,
        watering_schedule=watering_schedule,
        plant_image=image_path
    )

    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)

    return new_plant


# 🌿 GET USER PLANTS
@router.get("/", response_model=List[UserPlantResponse])
def list_my_plants(

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)

):

    plants = (
        db.query(UserPlant, Plant.image_url)
        .outerjoin(Plant, UserPlant.plant_library_id == Plant.id)
        .filter(UserPlant.user_id == current_user.id)
        .order_by(UserPlant.id.desc())
        .all()
    )

    result = []

    for user_plant, library_image in plants:

        image = user_plant.plant_image if user_plant.plant_image else library_image

        result.append({
            "id": user_plant.id,
            "plant_name": user_plant.plant_name,
            "plant_type": user_plant.plant_type,
            "pot_size": user_plant.pot_size,
            "location": user_plant.location,
            "watering_schedule": user_plant.watering_schedule,
            "plant_image": image
        })

    return result


# ✏️ UPDATE PLANT
@router.put("/{plant_id}", response_model=UserPlantResponse)
async def update_my_plant(

    plant_id: int,

    plant_name: str = Form(...),
    plant_type: str = Form(None),
    pot_size: str = Form(None),
    location: str = Form(None),
    watering_schedule: str = Form(None),

    plant_image: UploadFile = File(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)

):

    plant = db.query(UserPlant).filter(
        UserPlant.id == plant_id,
        UserPlant.user_id == current_user.id
    ).first()

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    # ⭐ DUPLICATE CHECK
    duplicate = db.query(UserPlant).filter(
        UserPlant.user_id == current_user.id,
        UserPlant.plant_name == plant_name,
        UserPlant.location == location,
        UserPlant.id != plant_id
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Another plant with same name and location already exists"
        )

    # ⭐ CHECK IF ANY CHANGE
    if (
        plant.plant_name == plant_name and
        plant.plant_type == plant_type and
        plant.pot_size == pot_size and
        plant.location == location and
        plant.watering_schedule == watering_schedule and
        plant_image is None
    ):
        raise HTTPException(
            status_code=400,
            detail="No record updated"
        )

    plant.plant_name = plant_name
    plant.plant_type = plant_type
    plant.pot_size = pot_size
    plant.location = location
    plant.watering_schedule = watering_schedule

    # ✅ CLOUDINARY UPDATE
    if plant_image:

        print("NEW CODE RUNNING")
        print("CONTENT TYPE:", plant_image.content_type)

        if not plant_image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type")

        try:
            result = cloudinary.uploader.upload(plant_image.file)
            plant.plant_image = result["secure_url"]

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    db.commit()
    db.refresh(plant)

    return plant


# 🗑️ DELETE PLANT
@router.delete("/{plant_id}")
def delete_my_plant(

    plant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)

):

    plant = db.query(UserPlant).filter(
        UserPlant.id == plant_id,
        UserPlant.user_id == current_user.id
    ).first()

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    # ❌ Removed local file deletion (not needed anymore)

    db.delete(plant)
    db.commit()

    return {"message": "Plant deleted successfully"}


# 🌿 ADD FROM LIBRARY
@router.post("/add-from-library/{plant_id}")
def add_from_library(
    plant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    plant = db.query(Plant).filter(Plant.id == plant_id).first()

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    existing = db.query(UserPlant).filter(
        UserPlant.user_id == current_user.id,
        UserPlant.plant_library_id == plant_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Plant already exists in your garden"
        )

    user_plant = UserPlant(
        user_id=current_user.id,
        plant_library_id=plant.id,
        plant_name=plant.name,
        plant_type=plant.category,
        pot_size=plant.recommended_pot_size,
        location=plant.light,
        watering_schedule=plant.water_requirement
    )

    db.add(user_plant)
    db.commit()
    db.refresh(user_plant)

    return {"message": "Plant added to My Garden 🌱"}