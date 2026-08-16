from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user, require_role
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
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    return await create_notification(
        notification_data.model_dump()
    )


@router.get(
    "/",
    response_model=list[NotificationResponse],
)
async def get_notifications(
    user_id: str,
    current_user: dict = Depends(get_current_user),
):
    # Admin can view notifications for any user.
    if current_user["role"] != "admin":
        if user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own notifications",
            )

    return await get_all_notifications(user_id)


@router.post(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
async def mark_as_read(
    notification_id: str,
    current_user: dict = Depends(
        require_role("admin", "parent")
    ),
):
    result = await mark_notification_as_read(
        notification_id,
        current_user["id"],
        current_user["role"],
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return result