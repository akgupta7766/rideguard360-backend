from pydantic import BaseModel, Field


class RouteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class RouteUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class RouteResponse(BaseModel):
    id: str
    name: str
    description: str | None = None