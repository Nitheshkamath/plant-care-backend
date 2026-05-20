from sqlalchemy.orm import Session

from fastapi import HTTPException

from app.models.user import User

from app.core.security import (

    hash_password,

    verify_password,

    create_access_token,

    create_refresh_token
)


# ---------------------------------------------------
# REGISTER USER
# ---------------------------------------------------
def register_user(
        db: Session,
        user
):

    existing = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing:

        raise HTTPException(

            status_code=400,

            detail="User already exists"
        )

    new_user = User(

        email=user.email,

        password=hash_password(
            user.password
        )
    )

    db.add(new_user)

    db.commit()

    return {

        "message":
        "User registered successfully"
    }


# ---------------------------------------------------
# LOGIN USER
# ---------------------------------------------------
def login_user(
        db: Session,
        data
):

    user = db.query(User).filter(
        User.email == data.email
    ).first()

    # INVALID EMAIL
    if not user:

        raise HTTPException(

            status_code=401,

            detail=(
                "Invalid email or password"
            )
        )

    # INVALID PASSWORD
    if not verify_password(
            data.password,
            user.password
    ):

        raise HTTPException(

            status_code=401,

            detail=(
                "Invalid email or password"
            )
        )

    # 🔥 ACCESS TOKEN
    access_token = (
        create_access_token(user)
    )

    # 🔥 REFRESH TOKEN
    refresh_token = (
        create_refresh_token(user)
    )

    # SAVE REFRESH TOKEN
    user.refresh_token = (
        refresh_token
    )

    db.commit()

    return {

        "access_token":
        access_token,

        "refresh_token":
        refresh_token,

        "token_type":
        "bearer"
    }