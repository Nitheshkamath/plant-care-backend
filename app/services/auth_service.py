from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_token
from fastapi import HTTPException

def register_user(db: Session, user):
    existing = db.query(User).filter(User.email == user.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="User exists")

    new_user = User(
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()

    return {"message": "User registered"}

def login_user(db: Session, data):

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user)

    return {
        "access_token": token,
        "token_type": "bearer"
    }