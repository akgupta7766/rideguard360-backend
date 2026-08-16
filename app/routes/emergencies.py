from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_role
from app.schemas.emergency import (
    EmergencyCreate,
    EmergencyResponse,
)
from app.services.emergency_service import (
    create_emergency,
    get_active_emergencies,
    get_emergency_by_id,
    resolve_emergency,
)


router = APIRouter(
    prefix="/api/emergencies",
    tags=["Emergencies"],
)


@router.post(
    "",
    response_model=EmergencyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_emergency_endpoint(
    data: EmergencyCreate,
    current_user: dict = Depends(
        require_role("admin", "driver")
    ),
):
    result = await create_emergency(
        data.model_dump()
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found",
        )

    return result


@router.get(
    "/active",
    response_model=list[EmergencyResponse],
)
async def get_active_emergencies_endpoint(
    current_user: dict = Depends(
        require_role("admin", "driver", "parent")
    ),
):
    return await get_active_emergencies()


@router.get(
    "/{emergency_id}",
    response_model=EmergencyResponse,
)
async def get_emergency_endpoint(
    emergency_id: str,
    current_user: dict = Depends(
        require_role("admin", "driver", "parent")
    ),
):
    result = await get_emergency_by_id(
        emergency_id
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency not found",
        )

    return result


@router.post(
    "/{emergency_id}/resolve",
    response_model=EmergencyResponse,
)
async def resolve_emergency_endpoint(
    emergency_id: str,
    current_user: dict = Depends(
        require_role("admin", "driver")
    ),
):
    result = await resolve_emergency(
        emergency_id
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency not found",
        )

    return result