from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes import auth_routes
from app.routes import user_routes, plant_routes
from app.routes import user_plant_routes
from app.routes import reminder_routes
from app.routes import care_histroy_routes
from app.database.base import create_tables


app = FastAPI()

# ---------- CORS FIX ----------
origins = [
    "https://plant-mate-785ab.web.app",
    "https://plant-mate-785ab.firebaseapp.com",
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     # allow these domains
    allow_credentials=True,
    allow_methods=["*"],       # allow all methods (GET, POST, etc.)
    allow_headers=["*"],       # allow all headers
)

# ---------- Create tables ----------
create_tables()

# ---------- Routers ----------
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(plant_routes.router)
app.include_router(reminder_routes.router)
app.include_router(care_histroy_routes.router)
app.include_router(user_plant_routes.router, tags=["User plants"])

# ---------- Static uploads ----------
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")