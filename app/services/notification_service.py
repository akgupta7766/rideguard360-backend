from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from app.database.mongodb import db


notifications_collection = db["notifications"]


def serialize_notification(notification: dict) -> dict:
    return {
        "id": str(notification["_id"]),
        "user_id": notification["user_id"],
        "title": notification["title"],
        "message": notification["message"],
        "notification_type": notification.get(
            "notification_type",
            "info",
        ),
        "is_read": notification.get("is_read", False),
        "created_at": notification["created_at"],
    }


async def create_notification(notification_data: dict):
    notification_data["is_read"] = False
    notification_data["created_at"] = datetime.now(timezone.utc)

    result = await notifications_collection.insert_one(
        notification_data
    )

    created_notification = await notifications_collection.find_one(
        {"_id": result.inserted_id}
    )

    return serialize_notification(created_notification)


async def get_all_notifications(user_id: str):
    notifications = []

    async for notification in notifications_collection.find(
        {"user_id": user_id}
    ).sort("created_at", -1):
        notifications.append(
            serialize_notification(notification)
        )

    return notifications


async def mark_notification_as_read(notification_id: str):
    try:
        object_id = ObjectId(notification_id)
    except InvalidId:
        return None

    notification = await notifications_collection.find_one(
        {"_id": object_id}
    )

    if not notification:
        return None

    await notifications_collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "is_read": True
            }
        },
    )

    updated_notification = await notifications_collection.find_one(
        {"_id": object_id}
    )

    return serialize_notification(updated_notification)