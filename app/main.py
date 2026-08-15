from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb_connection,
)
from app.routes.auth import router as auth_router


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


app.include_router(auth_router)


@app.get("/")
async def root():
    return {
        "message": "RideGuard 360 API is running",
        "status": "success",
    }