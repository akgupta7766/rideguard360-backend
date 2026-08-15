from bson import ObjectId
from bson.errors import InvalidId

from app.database.mongodb import db


routes_collection = db["routes"]
stops_collection = db["stops"]


def serialize_route(route: dict) -> dict:
    return {
        "id": str(route["_id"]),
        "name": route["name"],
        "description": route.get("description"),
    }


def serialize_stop(stop: dict) -> dict:
    return {
        "id": str(stop["_id"]),
        "route_id": stop["route_id"],
        "name": stop["name"],
        "latitude": stop["latitude"],
        "longitude": stop["longitude"],
        "sequence": stop["sequence"],
    }


async def create_route(route_data: dict):
    existing = await routes_collection.find_one(
        {"name": route_data["name"]}
    )

    if existing:
        return None

    result = await routes_collection.insert_one(route_data)

    route = await routes_collection.find_one(
        {"_id": result.inserted_id}
    )

    return serialize_route(route)


async def get_all_routes():
    routes = []

    async for route in routes_collection.find().sort("name", 1):
        routes.append(serialize_route(route))

    return routes


async def get_route_by_id(route_id: str):
    try:
        route_object_id = ObjectId(route_id)
    except InvalidId:
        return None

    route = await routes_collection.find_one(
        {"_id": route_object_id}
    )

    if not route:
        return None

    return serialize_route(route)


async def update_route(
    route_id: str,
    update_data: dict,
):
    try:
        route_object_id = ObjectId(route_id)
    except InvalidId:
        return None

    update_data = {
        key: value
        for key, value in update_data.items()
        if value is not None
    }

    if update_data:
        await routes_collection.update_one(
            {"_id": route_object_id},
            {"$set": update_data},
        )

    return await get_route_by_id(route_id)


async def create_stop(
    route_id: str,
    stop_data: dict,
):
    try:
        route_object_id = ObjectId(route_id)
    except InvalidId:
        return None

    route = await routes_collection.find_one(
        {"_id": route_object_id}
    )

    if not route:
        return None

    # Store the route ID as a string so it matches the API contract.
    stop_data["route_id"] = route_id

    # Prevent duplicate stop sequence numbers on the same route.
    existing_stop = await stops_collection.find_one(
        {
            "route_id": route_id,
            "sequence": stop_data["sequence"],
        }
    )

    if existing_stop:
        return "duplicate_sequence"

    result = await stops_collection.insert_one(stop_data)

    stop = await stops_collection.find_one(
        {"_id": result.inserted_id}
    )

    return serialize_stop(stop)


async def get_route_stops(route_id: str):
    try:
        route_object_id = ObjectId(route_id)
    except InvalidId:
        return None

    route = await routes_collection.find_one(
        {"_id": route_object_id}
    )

    if not route:
        return None

    stops = []

    async for stop in stops_collection.find(
        {"route_id": route_id}
    ).sort("sequence", 1):
        stops.append(serialize_stop(stop))

    return stops


async def update_stop(
    stop_id: str,
    update_data: dict,
):
    try:
        stop_object_id = ObjectId(stop_id)
    except InvalidId:
        return None

    update_data = {
        key: value
        for key, value in update_data.items()
        if value is not None
    }

    if update_data:
        await stops_collection.update_one(
            {"_id": stop_object_id},
            {"$set": update_data},
        )

    stop = await stops_collection.find_one(
        {"_id": stop_object_id}
    )

    if not stop:
        return None

    return serialize_stop(stop)