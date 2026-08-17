from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from app.database.mongodb import db
from app.websocket.manager import manager


gps_collection = db["gps_locations"]
buses_collection = db["buses"]


def serialize_gps(data: dict) -> dict:
    return {
        "bus_id": data["bus_id"],
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "speed": data.get("speed", 0),
        "heading": data.get("heading"),
        "timestamp": data["timestamp"],
    }


async def update_bus_location(gps_data: dict):
    # Convert incoming bus_id into MongoDB ObjectId
    try:
        bus_object_id = ObjectId(gps_data["bus_id"])
    except InvalidId:
        return None

    # Check that the bus exists
    bus = await buses_collection.find_one(
        {"_id": bus_object_id}
    )

    if not bus:
        return None

    # Add current UTC timestamp
    gps_data["timestamp"] = datetime.now(timezone.utc)

    # Save latest location
    await gps_collection.update_one(
        {"bus_id": gps_data["bus_id"]},
        {"$set": gps_data},
        upsert=True,
    )

    # Get saved location
    saved_location = await gps_collection.find_one(
        {"bus_id": gps_data["bus_id"]}
    )

    location = serialize_gps(saved_location)

    # Broadcast live location to connected clients
    await manager.broadcast(
        {
            "type": "bus_location",
            "data": location,
        }
    )

    return location


async def get_bus_location(bus_id: str):
    location = await gps_collection.find_one(
        {"bus_id": bus_id}
    )

    if not location:
        return None

    return serialize_gps(location)