from datetime import datetime

from pydantic import BaseModel, Field


class TripStartRequest(BaseModel):
    bus_id: str
    route_id: str


class TripResponse(BaseModel):
    id: str
    bus_id: str
    route_id: str
    status: str
    started_at: datetime
    ended_at: datetime | None = None