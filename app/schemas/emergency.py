from datetime import datetime

from pydantic import BaseModel, Field


class EmergencyCreate(BaseModel):
    bus_id: str
    emergency_type: str = Field(..., min_length=1, max_length=50)
    message: str | None = Field(default=None, max_length=500)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class EmergencyResponse(BaseModel):
    id: str
    bus_id: str
    emergency_type: str
    message: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: str
    created_at: datetime
    resolved_at: datetime | None = None