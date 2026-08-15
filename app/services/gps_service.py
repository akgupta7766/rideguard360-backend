from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from app.database.mongodb import db


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
    # Convert the incoming bus_id into MongoDB ObjectId
    try:
        bus_object_id = ObjectId(gps_data["bus_id"])
    except InvalidId:
        return None

    # Check that the bus actually exists
    bus = await buses_collection.find_one(
        {"_id": bus_object_id}
    )

    if not bus:
        return None

    gps_data["timestamp"] = datetime.now(timezone.utc)

    await gps_collection.update_one(
        {"bus_id": gps_data["bus_id"]},
        {"$set": gps_data},
        upsert=True,
    )

    saved_location = await gps_collection.find_one(
        {"bus_id": gps_data["bus_id"]}
    )

    return serialize_gps(saved_location)


async def get_bus_location(bus_id: str):
    location = await gps_collection.find_one(
        {"bus_id": bus_id}
    )

    if not location:
        return None

    return serialize_gps(location)