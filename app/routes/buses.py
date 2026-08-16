from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_role
from app.services.bus_service import (
    create_bus,
    get_all_buses,
    get_bus_by_id,
    update_bus,
    delete_bus,
)


router = APIRouter(
    prefix="/api/buses",
    tags=["Buses"],
)


@router.post("/")
async def create_new_bus(
    bus_data: dict,
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    result = await create_bus(bus_data)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bus number or registration number already exists",
        )

    return result


@router.get("/")
async def get_buses(
    current_user: dict = Depends(
        require_role("admin", "driver", "parent")
    ),
):
    return await get_all_buses()


@router.get("/{bus_id}")
async def get_bus(
    bus_id: str,
    current_user: dict = Depends(
        require_role("admin", "driver", "parent")
    ),
):
    result = await get_bus_by_id(bus_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found",
        )

    return result


@router.put("/{bus_id}")
async def update_existing_bus(
    bus_id: str,
    bus_data: dict,
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    result = await update_bus(
        bus_id,
        bus_data,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found",
        )

    return result


@router.delete("/{bus_id}")
async def delete_existing_bus(
    bus_id: str,
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    result = await delete_bus(bus_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found",
        )

    return {
        "message": "Bus deleted successfully",
    }