from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from app.database.mongodb import db


boarding_collection = db["boarding"]
trips_collection = db["trips"]
stops_collection = db["stops"]


def serialize_boarding(record: dict) -> dict:
    return {
        "id": str(record["_id"]),
        "trip_id": record["trip_id"],
        "student_id": record["student_id"],
        "stop_id": record["stop_id"],
        "action": record["action"],
        "timestamp": record["timestamp"],
    }


async def create_boarding(boarding_data: dict):
    trip_id = boarding_data["trip_id"]
    stop_id = boarding_data["stop_id"]
    student_id = boarding_data["student_id"]

    # Validate trip ID
    try:
        trip_object_id = ObjectId(trip_id)
    except InvalidId:
        return "trip_not_found"

    # Validate stop ID
    try:
        stop_object_id = ObjectId(stop_id)
    except InvalidId:
        return "stop_not_found"

    # Trip must exist
    trip = await trips_collection.find_one(
        {"_id": trip_object_id}
    )

    if not trip:
        return "trip_not_found"

    # Stop must exist
    stop = await stops_collection.find_one(
        {"_id": stop_object_id}
    )

    if not stop:
        return "stop_not_found"

    # Stop must belong to the route of this trip
    if stop.get("route_id") != trip.get("route_id"):
        return "stop_not_on_trip_route"

    # Prevent duplicate boarding action for the same student,
    # trip and stop.
    existing = await boarding_collection.find_one(
        {
            "trip_id": trip_id,
            "student_id": student_id,
            "stop_id": stop_id,
            "action": boarding_data["action"],
        }
    )

    if existing:
        return "duplicate"

    boarding_data["timestamp"] = datetime.now(timezone.utc)

    result = await boarding_collection.insert_one(
        boarding_data
    )

    created_record = await boarding_collection.find_one(
        {"_id": result.inserted_id}
    )

    return serialize_boarding(created_record)


async def get_boarding_by_stop(stop_id: str):
    records = []

    async for record in boarding_collection.find(
        {"stop_id": stop_id}
    ).sort("timestamp", 1):
        records.append(
            serialize_boarding(record)
        )

    return records


async def get_boarding_by_trip(trip_id: str):
    records = []

    async for record in boarding_collection.find(
        {"trip_id": trip_id}
    ).sort("timestamp", 1):
        records.append(
            serialize_boarding(record)
        )

    return records