from datetime import datetime

from pydantic import BaseModel, Field


class GPSUpdateRequest(BaseModel):
    bus_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed: float = Field(default=0, ge=0)
    heading: float | None = Field(default=None, ge=0, le=360)


class GPSResponse(BaseModel):
    bus_id: str
    latitude: float
    longitude: float
    speed: float
    heading: float | None = None
    timestamp: datetime