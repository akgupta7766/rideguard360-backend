from bson import ObjectId
from bson.errors import InvalidId

from app.database.mongodb import db


drivers_collection = db["drivers"]


def serialize_driver(driver: dict) -> dict:
    return {
        "id": str(driver["_id"]),
        "name": driver["name"],
        "email": driver["email"],
        "phone": driver["phone"],
        "license_number": driver["license_number"],
        "status": driver.get("status", "active"),
    }


async def create_driver(driver_data: dict):
    existing = await drivers_collection.find_one(
        {
            "$or": [
                {"email": driver_data["email"]},
                {"license_number": driver_data["license_number"]},
            ]
        }
    )

    if existing:
        return None

    result = await drivers_collection.insert_one(driver_data)

    created_driver = await drivers_collection.find_one(
        {"_id": result.inserted_id}
    )

    return serialize_driver(created_driver)


async def get_all_drivers():
    drivers = []

    async for driver in drivers_collection.find().sort("name", 1):
        drivers.append(serialize_driver(driver))

    return drivers


async def get_driver_by_id(driver_id: str):
    try:
        object_id = ObjectId(driver_id)
    except InvalidId:
        return None

    driver = await drivers_collection.find_one(
        {"_id": object_id}
    )

    if not driver:
        return None

    return serialize_driver(driver)


async def update_driver(driver_id: str, update_data: dict):
    try:
        object_id = ObjectId(driver_id)
    except InvalidId:
        return None

    update_data = {
        key: value
        for key, value in update_data.items()
        if value is not None
    }

    if not update_data:
        return await get_driver_by_id(driver_id)

    await drivers_collection.update_one(
        {"_id": object_id},
        {"$set": update_data},
    )

    return await get_driver_by_id(driver_id)


async def delete_driver(driver_id: str):
    try:
        object_id = ObjectId(driver_id)
    except InvalidId:
        return False

    result = await drivers_collection.delete_one(
        {"_id": object_id}
    )

    return result.deleted_count > 0