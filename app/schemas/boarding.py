from datetime import datetime

from pydantic import BaseModel, Field


class BoardingCreate(BaseModel):
    trip_id: str
    student_id: str
    stop_id: str
    action: str = Field(..., pattern="^(boarded|dropped)$")


class BoardingResponse(BaseModel):
    id: str
    trip_id: str
    student_id: str
    stop_id: str
    action: str
    timestamp: datetime