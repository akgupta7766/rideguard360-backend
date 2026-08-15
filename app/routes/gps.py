from fastapi import APIRouter, HTTPException, status

from app.schemas.gps import GPSUpdateRequest, GPSResponse
from app.services.gps_service import (
    update_bus_location,
    get_bus_location,
)


router = APIRouter(
    prefix="/api/gps",
    tags=["GPS"],
)


@router.post(
    "/update",
    response_model=GPSResponse,
)
async def update_gps(data: GPSUpdateRequest):
    result = await update_bus_location(
        data.model_dump()
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found",
        )

    return result


@router.get(
    "/bus/{bus_id}",
    response_model=GPSResponse,
)
async def get_gps(bus_id: str):
    result = await get_bus_location(bus_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GPS location not found for this bus",
        )

    return result