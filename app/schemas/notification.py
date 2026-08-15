from datetime import datetime

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    notification_type: str = "info"


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime