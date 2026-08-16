from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_role
from app.schemas.driver import (
    DriverCreate,
    DriverResponse,
    DriverUpdate,
)
from app.services.driver_service import (
    create_driver,
    get_all_drivers,
    get_driver_by_id,
    update_driver,
    delete_driver,
)


router = APIRouter(
    prefix="/api/drivers",
    tags=["Drivers"],
)


@router.post(
    "/",
    response_model=DriverResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_driver(
    driver_data: DriverCreate,
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    result = await create_driver(
        driver_data.model_dump()
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Driver email or license number already exists",
        )

    return result


@router.get(
    "/",
    response_model=list[DriverResponse],
)
async def get_drivers(
    current_user: dict = Depends(
        require_role("admin", "driver")
    ),
):
    return await get_all_drivers()


@router.get(
    "/{driver_id}",
    response_model=DriverResponse,
)
async def get_driver(
    driver_id: str,
    current_user: dict = Depends(
        require_role("admin", "driver")
    ),
):
    result = await get_driver_by_id(driver_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found",
        )

    return result


@router.put(
    "/{driver_id}",
    response_model=DriverResponse,
)
async def update_existing_driver(
    driver_id: str,
    driver_data: DriverUpdate,
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    result = await update_driver(
        driver_id,
        driver_data.model_dump(exclude_none=True),
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found",
        )

    return result


@router.delete(
    "/{driver_id}",
)
async def delete_existing_driver(
    driver_id: str,
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    result = await delete_driver(driver_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found",
        )

    return {
        "message": "Driver deleted successfully"
    }