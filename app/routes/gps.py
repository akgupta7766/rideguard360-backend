from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from app.core.security import require_gps_update_access, require_role
from app.schemas.gps import GPSUpdateRequest, GPSResponse
from app.services.gps_service import (
    update_bus_location,
    get_bus_location,
)
from app.websocket.manager import manager


router = APIRouter(
    prefix="/api/gps",
    tags=["GPS"],
)


@router.post(
    "/update",
    response_model=GPSResponse,
)
async def update_gps(
    data: GPSUpdateRequest,
    current_user: dict = Depends(require_gps_update_access),
):
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
async def get_gps(
    bus_id: str,
    current_user: dict = Depends(
        require_role("admin", "driver", "parent")
    ),
):
    result = await get_bus_location(bus_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GPS location not found for this bus",
        )

    return result


@router.websocket("/ws")
async def gps_websocket(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        pass

    finally:
        manager.disconnect(websocket)
