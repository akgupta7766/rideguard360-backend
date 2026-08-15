from typing import Optional

from pydantic import BaseModel, Field


class BusCreate(BaseModel):
    bus_number: str = Field(..., min_length=1, max_length=50)
    registration_number: str = Field(..., min_length=1, max_length=50)
    capacity: int = Field(..., gt=0)
    model: Optional[str] = None
    status: str = "active"


class BusUpdate(BaseModel):
    bus_number: Optional[str] = Field(None, min_length=1, max_length=50)
    registration_number: Optional[str] = Field(
        None, min_length=1, max_length=50
    )
    capacity: Optional[int] = Field(None, gt=0)
    model: Optional[str] = None
    status: Optional[str] = None


class BusResponse(BaseModel):
    id: str
    bus_number: str
    registration_number: str
    capacity: int
    model: Optional[str] = None
    status: str