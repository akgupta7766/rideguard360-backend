from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from app.database.mongodb import db


emergencies_collection = db["emergencies"]
buses_collection = db["buses"]


def serialize_emergency(emergency: dict) -> dict:
    return {
        "id": str(emergency["_id"]),
        "bus_id": emergency["bus_id"],
        "emergency_type": emergency["emergency_type"],
        "message": emergency.get("message"),
        "latitude": emergency.get("latitude"),
        "longitude": emergency.get("longitude"),
        "status": emergency.get("status", "active"),
        "created_at": emergency["created_at"],
        "resolved_at": emergency.get("resolved_at"),
    }


async def create_emergency(emergency_data: dict):
    # Verify that the bus exists
    try:
        bus_object_id = ObjectId(emergency_data["bus_id"])
    except InvalidId:
        return None

    bus = await buses_collection.find_one(
        {"_id": bus_object_id}
    )

    if not bus:
        return None

    emergency_data["status"] = "active"
    emergency_data["created_at"] = datetime.now(timezone.utc)
    emergency_data["resolved_at"] = None

    result = await emergencies_collection.insert_one(
        emergency_data
    )

    created_emergency = await emergencies_collection.find_one(
        {"_id": result.inserted_id}
    )

    return serialize_emergency(created_emergency)


async def get_active_emergencies():
    emergencies = []

    cursor = emergencies_collection.find(
        {"status": "active"}
    ).sort("created_at", -1)

    async for emergency in cursor:
        emergencies.append(
            serialize_emergency(emergency)
        )

    return emergencies


async def get_emergency_by_id(emergency_id: str):
    try:
        object_id = ObjectId(emergency_id)
    except InvalidId:
        return None

    emergency = await emergencies_collection.find_one(
        {"_id": object_id}
    )

    if not emergency:
        return None

    return serialize_emergency(emergency)


async def resolve_emergency(emergency_id: str):
    try:
        object_id = ObjectId(emergency_id)
    except InvalidId:
        return None

    emergency = await emergencies_collection.find_one(
        {"_id": object_id}
    )

    if not emergency:
        return None

    # Don't resolve an emergency that is already resolved
    if emergency.get("status") == "resolved":
        return serialize_emergency(emergency)

    resolved_at = datetime.now(timezone.utc)

    await emergencies_collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "status": "resolved",
                "resolved_at": resolved_at,
            }
        },
    )

    updated_emergency = await emergencies_collection.find_one(
        {"_id": object_id}
    )

    return serialize_emergency(updated_emergency)