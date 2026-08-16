import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb_connection,
)

from app.routes.auth import router as auth_router
from app.routes.buses import router as buses_router
from app.routes.drivers import router as drivers_router
from app.routes.students import router as students_router
from app.routes.parents import router as parents_router
from app.routes.notifications import router as notifications_router
from app.routes.gps import router as gps_router
from app.routes.emergencies import router as emergencies_router
from app.routes.trips import router as trips_router
from app.routes.routes import router as routes_router
from app.routes.boarding import router as boarding_router


load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb()
    yield
    await close_mongodb_connection()


app = FastAPI(
    title="RideGuard 360 API",
    description="School Transport Safety Console Backend",
    version="1.0.0",
    lifespan=lifespan,
)


# ==========================================
# CORS
# ==========================================

frontend_urls = os.getenv(
    "FRONTEND_URLS",
    "http://localhost:5173,http://localhost:5174,"
    "http://127.0.0.1:5173,http://127.0.0.1:5174",
)

allow_origins = [
    url.strip()
    for url in frontend_urls.split(",")
    if url.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# ROUTERS
# ==========================================

app.include_router(auth_router)
app.include_router(buses_router)
app.include_router(drivers_router)
app.include_router(students_router)
app.include_router(parents_router)
app.include_router(notifications_router)
app.include_router(gps_router)
app.include_router(emergencies_router)
app.include_router(trips_router)
app.include_router(routes_router)
app.include_router(boarding_router)


# ==========================================
# ROOT
# ==========================================

@app.get("/")
async def root():
    return {
        "message": "RideGuard 360 API is running",
        "status": "success",
        "version": "1.0.0",
    }