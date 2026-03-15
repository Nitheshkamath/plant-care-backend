import os
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.db import SessionLocal
from app.models.user import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"))

security = HTTPBearer()

# ---------------- DB SESSION ---------------- #

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- PASSWORD ---------------- #

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)

# ---------------- JWT TOKEN ---------------- #

def create_token(user):

    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ---------------- OTP ---------------- #

def generate_otp():
    return str(random.randint(100000, 999999))

# ---------------- CURRENT USER ---------------- #

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials
    payload = decode_token(token)

    user_id = payload.get("user_id")
    email = payload.get("email")

    if user_id:
        user = db.query(User).filter(User.id == user_id).first()

    elif email:
        user = db.query(User).filter(User.email == email).first()

    else:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user