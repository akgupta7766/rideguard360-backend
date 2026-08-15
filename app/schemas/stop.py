from pydantic import BaseModel, Field


class StopCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    sequence: int = Field(..., ge=1)


class StopResponse(BaseModel):
    id: str
    route_id: str
    name: str
    latitude: float
    longitude: float
    sequence: int