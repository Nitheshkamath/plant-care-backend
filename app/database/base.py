from app.database.db import engine
from app.models.user import User

def create_tables():
    User.metadata.create_all(bind=engine)