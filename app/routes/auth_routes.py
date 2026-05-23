from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user_schema import (
    UserRegister,
    UserLogin
)

from app.services.auth_service import login_user

from app.database.db import SessionLocal

from google.oauth2 import id_token
from google.auth.transport import requests

from app.models.user import User

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    generate_otp,
    get_current_user
)

from datetime import datetime, timedelta

from app.core.email_utils import send_otp_email

import os

router = APIRouter()

GOOGLE_CLIENT_ID = (
    "22829050880-al22ksa461i63106tkr1j193lpdg41kt.apps.googleusercontent.com"
)

# ---------------------------------------------------
# DATABASE DEPENDENCY
# ---------------------------------------------------
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ---------------------------------------------------
# REGISTER
# ---------------------------------------------------
@router.post("/register")
def register(
        user: UserRegister,
        db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    new_user = User(

        name=user.name,

        email=user.email,

        password=hash_password(
            user.password
        )
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {

        "message":
        "User registered successfully"
    }


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------
@router.post("/login")
def login(
        user: UserLogin,
        db: Session = Depends(get_db)
):

    return login_user(db, user)


# ---------------------------------------------------
# GOOGLE LOGIN
# ---------------------------------------------------
@router.post("/google-login")
def google_login(
        data: dict,
        db: Session = Depends(get_db)
):

    token = data.get("token")

    if not token:

        raise HTTPException(
            status_code=400,
            detail="Google token missing"
        )

    try:

        # VERIFY GOOGLE TOKEN
        idinfo = id_token.verify_oauth2_token(

            token,

            requests.Request(),

            GOOGLE_CLIENT_ID
        )

        # EXTRACT INFO
        email = idinfo.get("email")

        name = idinfo.get("name")

        picture = idinfo.get("picture")

        if not email:

            raise HTTPException(

                status_code=400,

                detail=(
                    "Email not found "
                    "in Google token"
                )
            )

        # CHECK USER EXISTS
        user = db.query(User).filter(
            User.email == email
        ).first()

        # CREATE USER
        if not user:

            user = User(

                email=email,

                password="google_user",

                name=name,

                picture=picture
            )

            db.add(user)

            db.commit()

            db.refresh(user)

        # 🔥 ACCESS TOKEN
        access_token = create_access_token(
            user
        )

        # 🔥 REFRESH TOKEN
        refresh_token = create_refresh_token(
            user
        )

        # SAVE REFRESH TOKEN
        user.refresh_token = refresh_token

        db.commit()

        return {

            "access_token":
            access_token,

            "refresh_token":
            refresh_token,

            "token_type":
            "bearer"
        }

    except ValueError as e:

        print(
            "Google token verification failed:",
            str(e)
        )

        raise HTTPException(

            status_code=401,

            detail="Invalid Google token"
        )

    except Exception as e:

        print(
            "Unexpected Google login error:",
            str(e)
        )

        raise HTTPException(

            status_code=500,

            detail="Google login failed"
        )


# ---------------------------------------------------
# REFRESH TOKEN
# ---------------------------------------------------
@router.post("/refresh-token")
def refresh_token(
        data: dict,
        db: Session = Depends(get_db)
):

    refresh_token = data.get(
        "refresh_token"
    )

    if not refresh_token:

        raise HTTPException(

            status_code=400,

            detail="Refresh token required"
        )

    payload = decode_token(
        refresh_token
    )

    token_type = payload.get("type")

    if token_type != "refresh":

        raise HTTPException(

            status_code=401,

            detail="Invalid refresh token"
        )

    user_id = payload.get("user_id")

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found"
        )

    # VERIFY TOKEN MATCHES DB
    if user.refresh_token != refresh_token:

        raise HTTPException(

            status_code=401,

            detail="Refresh token mismatch"
        )

    # CREATE NEW ACCESS TOKEN
    new_access_token = (
        create_access_token(user)
    )

    return {

        "access_token":
        new_access_token
    }

# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------
@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    current_user.refresh_token = None

    db.commit()

    return {
        "message": "Logged out successfully"
    }

# ---------------------------------------------------
# SEND OTP
# ---------------------------------------------------
@router.post("/send-otp")
def send_otp(
        data: dict,
        db: Session = Depends(get_db)
):

    print("👉 API HIT: /send-otp")

    email = data.get("email")

    print("👉 Email:", email)

    print(
        "👉 MAIL_USERNAME:",
        os.getenv("MAIL_USERNAME")
    )

    print(
        "👉 MAIL_SERVER:",
        os.getenv("MAIL_SERVER")
    )

    print(
        "👉 MAIL_PORT:",
        os.getenv("MAIL_PORT")
    )

    if not email:

        raise HTTPException(

            status_code=400,

            detail="Email required"
        )

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found"
        )

    otp = generate_otp()

    user.reset_otp = otp

    user.otp_expiry = (
            datetime.utcnow()
            + timedelta(minutes=5)
    )

    db.commit()

    # SEND EMAIL
    print("👉 Calling send_otp_email()")

    send_otp_email(
        email,
        otp,
        user.name
    )

    print("✅ OTP process completed")

    return {

        "message":
        (
            "OTP sent to your email. "
            "Please check your inbox."
        )
    }


# ---------------------------------------------------
# VERIFY OTP + RESET PASSWORD
# ---------------------------------------------------
@router.post("/verify-otp")
def verify_otp(
        data: dict,
        db: Session = Depends(get_db)
):

    email = data.get("email")

    otp = data.get("otp")

    new_password = data.get(
        "new_password"
    )

    if (
            not email
            or not otp
            or not new_password
    ):

        raise HTTPException(

            status_code=400,

            detail="All fields required"
        )

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found"
        )

    # OTP EXISTS
    if (
            not user.reset_otp
            or not user.otp_expiry
    ):

        raise HTTPException(

            status_code=400,

            detail="No OTP requested"
        )

    # INVALID OTP
    if user.reset_otp != otp:

        raise HTTPException(

            status_code=400,

            detail="Invalid OTP"
        )

    # OTP EXPIRED
    if user.otp_expiry < datetime.utcnow():

        raise HTTPException(

            status_code=400,

            detail="OTP expired"
        )

    # UPDATE PASSWORD
    user.password = hash_password(
        new_password
    )

    # CLEAR OTP
    user.reset_otp = None

    user.otp_expiry = None

    db.commit()

    return {

        "message":
        "Password reset successful"
    }