import asyncio

from app.core.security import hash_password
from app.database.mongodb import db


async def create_admin():
    users = db["users"]

    existing = await users.find_one(
        {"email": "admin@rideguard.com"}
    )

    if existing:
        print("Admin already exists.")
        return

    admin = {
        "name": "Transport Admin",
        "email": "admin@rideguard.com",
        "password_hash": hash_password("Admin@123"),
        "role": "admin",
        "is_active": True,
    }

    result = await users.insert_one(admin)

    print("Admin created:", result.inserted_id)


asyncio.run(create_admin())