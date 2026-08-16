from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_role
from app.schemas.boarding import (
    BoardingCreate,
    BoardingResponse,
)
from app.services.boarding_service import (
    create_boarding,
    get_boarding_by_stop,
    get_boarding_by_trip,
)


router = APIRouter(
    prefix="/api/boarding",
    tags=["Boarding"],
)


@router.post(
    "",
    response_model=BoardingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_boarding_endpoint(
    data: BoardingCreate,
    current_user: dict = Depends(
        require_role("admin", "driver")
    ),
):
    result = await create_boarding(
        data.model_dump()
    )

    if result == "trip_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    if result == "stop_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stop not found",
        )

    if result == "student_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    if result == "stop_not_on_trip_route":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stop does not belong to the trip route",
        )

    if result == "duplicate":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate boarding event",
        )

    return result


@router.get(
    "/stop/{stop_id}",
    response_model=list[BoardingResponse],
)
async def get_boarding_for_stop(
    stop_id: str,
    current_user: dict = Depends(
        require_role("admin", "driver", "parent")
    ),
):
    return await get_boarding_by_stop(stop_id)


@router.get(
    "/trip/{trip_id}",
    response_model=list[BoardingResponse],
)
async def get_boarding_for_trip(
    trip_id: str,
    current_user: dict = Depends(
        require_role("admin", "driver", "parent")
    ),
):
    return await get_boarding_by_trip(trip_id)