from fastapi import FastAPI
from app.routes import auth_routes
from app.database.base import create_tables
from app.routes import user_routes,plant_routes
from app.routes import user_plant_routes
from app.routes import reminder_routes
from app.routes import care_histroy_routes

from fastapi.staticfiles import StaticFiles



app = FastAPI()

create_tables()

app.include_router(auth_routes.router,)
app.include_router(user_routes.router)
app.include_router(plant_routes.router)
app.include_router(reminder_routes.router)
app.include_router(care_histroy_routes.router)


app.include_router(user_plant_routes.router,tags=["User plants"])

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")