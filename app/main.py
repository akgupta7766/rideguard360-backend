from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb_connection,
)

from app.routes.auth import router as auth_router
from app.routes.buses import router as buses_router
from app.routes.gps import router as gps_router
from app.routes.emergencies import router as emergencies_router
from app.routes.trips import router as trips_router
from app.routes.routes import router as routes_router
from app.routes.boarding import router as boarding_router


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


# Register routers
app.include_router(auth_router)
app.include_router(buses_router)
app.include_router(gps_router)
app.include_router(emergencies_router)
app.include_router(trips_router)
app.include_router(routes_router)
app.include_router(boarding_router)

@app.get("/")
async def root():
    return {
        "message": "RideGuard 360 API is running",
        "status": "success",
    }