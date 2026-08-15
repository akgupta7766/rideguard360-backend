from bson import ObjectId
from bson.errors import InvalidId

from app.database.mongodb import db


students_collection = db["students"]


def serialize_student(student: dict) -> dict:
    return {
        "id": str(student["_id"]),
        "name": student["name"],
        "email": student["email"],
        "phone": student["phone"],
        "student_id": student["student_id"],
        "grade": student["grade"],
        "section": student["section"],
        "parent_id": student.get("parent_id"),
        "status": student.get("status", "active"),
    }


async def create_student(student_data: dict):
    existing = await students_collection.find_one(
        {
            "$or": [
                {"email": student_data["email"]},
                {"student_id": student_data["student_id"]},
            ]
        }
    )

    if existing:
        return None

    result = await students_collection.insert_one(student_data)

    created_student = await students_collection.find_one(
        {"_id": result.inserted_id}
    )

    return serialize_student(created_student)


async def get_all_students():
    students = []

    async for student in students_collection.find().sort("name", 1):
        students.append(serialize_student(student))

    return students


async def get_student_by_id(student_id: str):
    try:
        object_id = ObjectId(student_id)
    except InvalidId:
        return None

    student = await students_collection.find_one(
        {"_id": object_id}
    )

    if not student:
        return None

    return serialize_student(student)


async def update_student(student_id: str, update_data: dict):
    try:
        object_id = ObjectId(student_id)
    except InvalidId:
        return None

    update_data = {
        key: value
        for key, value in update_data.items()
        if value is not None
    }

    if not update_data:
        return await get_student_by_id(student_id)

    await students_collection.update_one(
        {"_id": object_id},
        {"$set": update_data},
    )

    return await get_student_by_id(student_id)


async def delete_student(student_id: str):
    try:
        object_id = ObjectId(student_id)
    except InvalidId:
        return False

    result = await students_collection.delete_one(
        {"_id": object_id}
    )

    return result.deleted_count > 0