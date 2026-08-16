from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_role
from app.schemas.route import (
    RouteCreate,
    RouteResponse,
    RouteUpdate,
)
from app.schemas.stop import (
    StopCreate,
    StopResponse,
)
from app.services.route_service import (
    create_route,
    get_all_routes,
    get_route_by_id,
    update_route,
    create_stop,
    get_route_stops,
    update_stop,
)


router = APIRouter(
    prefix="/api",
    tags=["Routes & Stops"],
)


# -------------------------
# Routes
# -------------------------

@router.get(
    "/routes",
    response_model=list[RouteResponse],
)
async def get_routes(
    current_user: dict = Depends(
        require_role("admin", "driver", "parent")
    ),
):
    return await get_all_routes()


@router.get(
    "/routes/{route_id}",
    response_model=RouteResponse,
)
async def get_route(
    route_id: str,
    current_user: dict = Depends(
        require_role("admin", "driver", "parent")
    ),
):
    result = await get_route_by_id(route_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    return result


@router.post(
    "/routes",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_route_endpoint(
    data: RouteCreate,
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    result = await create_route(
        data.model_dump()
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A route with this name already exists",
        )

    return result


@router.put(
    "/routes/{route_id}",
    response_model=RouteResponse,
)
async def update_route_endpoint(
    route_id: str,
    data: RouteUpdate,
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    result = await update_route(
        route_id,
        data.model_dump(),
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    return result


# -------------------------
# Stops
# -------------------------

@router.get(
    "/routes/{route_id}/stops",
    response_model=list[StopResponse],
)
async def get_stops(
    route_id: str,
    current_user: dict = Depends(
        require_role("admin", "driver", "parent")
    ),
):
    result = await get_route_stops(route_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    return result


@router.post(
    "/routes/{route_id}/stops",
    response_model=StopResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_stop_endpoint(
    route_id: str,
    data: StopCreate,
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    result = await create_stop(
        route_id,
        data.model_dump(),
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    if result == "duplicate_sequence":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A stop with this sequence already exists on this route",
        )

    return result


@router.put(
    "/stops/{stop_id}",
    response_model=StopResponse,
)
async def update_stop_endpoint(
    stop_id: str,
    data: StopCreate,
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    result = await update_stop(
        stop_id,
        data.model_dump(),
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stop not found",
        )

    return result