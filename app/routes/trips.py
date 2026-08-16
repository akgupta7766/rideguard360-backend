from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_role
from app.schemas.trip import TripStartRequest, TripResponse
from app.services.trip_service import (
    start_trip,
    get_all_trips,
    get_trip_by_id,
    end_trip,
)


router = APIRouter(
    prefix="/api/trips",
    tags=["Trips"],
)


@router.get(
    "",
    response_model=list[TripResponse],
)
async def get_trips(
    current_user: dict = Depends(
        require_role("admin", "driver", "parent")
    ),
):
    return await get_all_trips()


@router.get(
    "/{trip_id}",
    response_model=TripResponse,
)
async def get_trip(
    trip_id: str,
    current_user: dict = Depends(
        require_role("admin", "driver", "parent")
    ),
):
    result = await get_trip_by_id(trip_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    return result


@router.post(
    "/start",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_trip_endpoint(
    data: TripStartRequest,
    current_user: dict = Depends(
        require_role("admin", "driver")
    ),
):
    result = await start_trip(
        data.model_dump()
    )

    if result == "bus_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found",
        )

    if result == "route_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    if result == "already_active":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This bus already has an active trip",
        )

    return result


@router.post(
    "/{trip_id}/end",
    response_model=TripResponse,
)
async def end_trip_endpoint(
    trip_id: str,
    current_user: dict = Depends(
        require_role("admin", "driver")
    ),
):
    result = await end_trip(trip_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    return result