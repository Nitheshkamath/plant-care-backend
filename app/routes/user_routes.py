from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from fastapi.security import (
    OAuth2PasswordBearer
)

from sqlalchemy.orm import Session

from app.database.db import (
    SessionLocal
)

from app.models.user import User

from app.core.security import (
    decode_token
)

router = APIRouter()

# ---------------------------------------------------
# OAUTH2 SCHEME
# ---------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
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
# GET CURRENT USER
# ---------------------------------------------------
@router.get("/me")
def get_me(

        token: str = Depends(
            oauth2_scheme
        ),

        db: Session = Depends(
            get_db
        )
):

    payload = decode_token(token)

    # 🔥 TOKEN TYPE CHECK
    token_type = payload.get("type")

    if token_type != "access":

        raise HTTPException(

            status_code=401,

            detail="Invalid access token"
        )

    user_id = payload.get("user_id")

    if not user_id:

        raise HTTPException(

            status_code=401,

            detail="Invalid token payload"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found"
        )

    return {

        "user": {

            "id": user.id,

            "name": user.name,

            "email": user.email,

            "picture": user.picture
        }
    }