from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.models.user import User
from app.core.security import decode_token

router = APIRouter()

# 🔐 OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 🗄 DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 👤 GET CURRENT USER
@router.get("/me")
def get_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    data = decode_token(token)

    user = db.query(User).filter(User.email == data["email"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user": {
            "name": user.name,
            "email": user.email,
            "picture": user.picture
        }
    }