from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ---------- Routes ----------
from app.routes import auth_routes
from app.routes import user_routes, plant_routes
from app.routes import user_plant_routes
from app.routes import reminder_routes
from app.routes import care_histroy_routes
from app.routes.devices_router import router as device_router  # 🔥 NEW

# ---------- Core ----------
from app.database.base import create_tables
from app.core.scheduler import run_scheduler  # 🔥 NEW

app = FastAPI()

# ---------- CORS ----------
origins = [
    "https://plant-mate-785ab.web.app",
    "https://plant-mate-785ab.firebaseapp.com",
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Startup ----------
@app.on_event("startup")
def startup_event():
    create_tables()       # ✅ ensure tables created
    run_scheduler()       # 🔥 start background job


# ---------- Routers ----------
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(plant_routes.router)
app.include_router(reminder_routes.router)
app.include_router(care_histroy_routes.router)
app.include_router(user_plant_routes.router, tags=["User plants"])
app.include_router(device_router)  # 🔥 NEW (FCM)


# ---------- Static ----------
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")