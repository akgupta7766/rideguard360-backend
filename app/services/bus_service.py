from bson import ObjectId
from bson.errors import InvalidId

from app.database.mongodb import db


buses_collection = db["buses"]


def serialize_bus(bus: dict) -> dict:
    return {
        "id": str(bus["_id"]),
        "bus_number": bus["bus_number"],
        "registration_number": bus["registration_number"],
        "capacity": bus["capacity"],
        "model": bus.get("model"),
        "status": bus.get("status", "active"),
    }


async def create_bus(bus_data: dict):
    existing = await buses_collection.find_one(
        {
            "$or": [
                {"bus_number": bus_data["bus_number"]},
                {"registration_number": bus_data["registration_number"]},
            ]
        }
    )

    if existing:
        return None

    result = await buses_collection.insert_one(bus_data)

    created_bus = await buses_collection.find_one(
        {"_id": result.inserted_id}
    )

    return serialize_bus(created_bus)


async def get_all_buses():
    buses = []

    async for bus in buses_collection.find().sort("bus_number", 1):
        buses.append(serialize_bus(bus))

    return buses


async def get_bus_by_id(bus_id: str):
    try:
        object_id = ObjectId(bus_id)
    except InvalidId:
        return None

    bus = await buses_collection.find_one({"_id": object_id})

    if not bus:
        return None

    return serialize_bus(bus)


async def update_bus(bus_id: str, update_data: dict):
    try:
        object_id = ObjectId(bus_id)
    except InvalidId:
        return None

    update_data = {
        key: value
        for key, value in update_data.items()
        if value is not None
    }

    if not update_data:
        return await get_bus_by_id(bus_id)

    await buses_collection.update_one(
        {"_id": object_id},
        {"$set": update_data},
    )

    return await get_bus_by_id(bus_id)


async def delete_bus(bus_id: str):
    try:
        object_id = ObjectId(bus_id)
    except InvalidId:
        return False

    result = await buses_collection.delete_one(
        {"_id": object_id}
    )

    return result.deleted_count > 0