from fastapi import APIRouter, HTTPException, status

from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
)
from app.services.notification_service import (
    create_notification,
    get_all_notifications,
    mark_notification_as_read,
)


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"],
)


@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_notification(
    notification_data: NotificationCreate,
):
    return await create_notification(
        notification_data.model_dump()
    )


@router.get(
    "/",
    response_model=list[NotificationResponse],
)
async def get_notifications(user_id: str):
    return await get_all_notifications(user_id)


@router.post(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
async def mark_as_read(notification_id: str):
    result = await mark_notification_as_read(
        notification_id
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return result