from bson import ObjectId
from bson.errors import InvalidId

from app.database.mongodb import db


parents_collection = db["parents"]


def serialize_parent(parent: dict) -> dict:
    return {
        "id": str(parent["_id"]),
        "name": parent["name"],
        "email": parent["email"],
        "phone": parent["phone"],
        "student_ids": parent.get("student_ids", []),
        "status": parent.get("status", "active"),
    }


async def create_parent(parent_data: dict):
    existing = await parents_collection.find_one(
        {"email": parent_data["email"]}
    )

    if existing:
        return None

    result = await parents_collection.insert_one(parent_data)

    created_parent = await parents_collection.find_one(
        {"_id": result.inserted_id}
    )

    return serialize_parent(created_parent)


async def get_all_parents():
    parents = []

    async for parent in parents_collection.find().sort("name", 1):
        parents.append(serialize_parent(parent))

    return parents


async def get_parent_by_id(parent_id: str):
    try:
        object_id = ObjectId(parent_id)
    except InvalidId:
        return None

    parent = await parents_collection.find_one(
        {"_id": object_id}
    )

    if not parent:
        return None

    return serialize_parent(parent)


async def update_parent(parent_id: str, update_data: dict):
    try:
        object_id = ObjectId(parent_id)
    except InvalidId:
        return None

    update_data = {
        key: value
        for key, value in update_data.items()
        if value is not None
    }

    if not update_data:
        return await get_parent_by_id(parent_id)

    await parents_collection.update_one(
        {"_id": object_id},
        {"$set": update_data},
    )

    return await get_parent_by_id(parent_id)


async def delete_parent(parent_id: str):
    try:
        object_id = ObjectId(parent_id)
    except InvalidId:
        return False

    result = await parents_collection.delete_one(
        {"_id": object_id}
    )

    return result.deleted_count > 0