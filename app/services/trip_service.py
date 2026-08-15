from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from app.database.mongodb import db


trips_collection = db["trips"]
buses_collection = db["buses"]
routes_collection = db["routes"]


def serialize_trip(trip: dict) -> dict:
    return {
        "id": str(trip["_id"]),
        "bus_id": trip["bus_id"],
        "route_id": trip["route_id"],
        "status": trip["status"],
        "started_at": trip["started_at"],
        "ended_at": trip.get("ended_at"),
    }


async def start_trip(trip_data: dict):
    # Validate bus ID
    try:
        bus_object_id = ObjectId(trip_data["bus_id"])
    except InvalidId:
        return "bus_not_found"

    # Validate route ID
    try:
        route_object_id = ObjectId(trip_data["route_id"])
    except InvalidId:
        return "route_not_found"

    # Verify bus exists
    bus = await buses_collection.find_one(
        {"_id": bus_object_id}
    )

    if not bus:
        return "bus_not_found"

    # Verify route exists
    route = await routes_collection.find_one(
        {"_id": route_object_id}
    )

    if not route:
        return "route_not_found"

    # Prevent another active trip for the same bus
    existing_trip = await trips_collection.find_one(
        {
            "bus_id": trip_data["bus_id"],
            "status": "active",
        }
    )

    if existing_trip:
        return "already_active"

    now = datetime.now(timezone.utc)

    trip = {
        "bus_id": trip_data["bus_id"],
        "route_id": trip_data["route_id"],
        "status": "active",
        "started_at": now,
        "ended_at": None,
    }

    result = await trips_collection.insert_one(trip)

    created_trip = await trips_collection.find_one(
        {"_id": result.inserted_id}
    )

    return serialize_trip(created_trip)


async def get_all_trips():
    trips = []

    async for trip in trips_collection.find().sort(
        "started_at", -1
    ):
        trips.append(serialize_trip(trip))

    return trips


async def get_trip_by_id(trip_id: str):
    try:
        object_id = ObjectId(trip_id)
    except InvalidId:
        return None

    trip = await trips_collection.find_one(
        {"_id": object_id}
    )

    if not trip:
        return None

    return serialize_trip(trip)


async def end_trip(trip_id: str):
    try:
        object_id = ObjectId(trip_id)
    except InvalidId:
        return None

    trip = await trips_collection.find_one(
        {"_id": object_id}
    )

    if not trip:
        return None

    # Don't end an already completed trip
    if trip.get("status") == "completed":
        return serialize_trip(trip)

    now = datetime.now(timezone.utc)

    await trips_collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "status": "completed",
                "ended_at": now,
            }
        },
    )

    updated_trip = await trips_collection.find_one(
        {"_id": object_id}
    )

    return serialize_trip(updated_trip)