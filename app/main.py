from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb_connection,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb()

    yield

    await close_mongodb_connection()


app = FastAPI(
    title="RideGuard 360 - School Transport Safety Console",
    description="Backend API for the Goblin Git SIH project",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "message": "RideGuard 360 Backend is running",
        "team": "Goblin Git",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }