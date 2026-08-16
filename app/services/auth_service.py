from typing import Optional

from passlib.context import CryptContext

from app.core.security import (
    create_access_token,
    hash_password,
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


async def register_user(
    users_collection,
    name: str,
    email: str,
    password: str,
    role: str,
) -> Optional[dict]:

    existing_user = await users_collection.find_one(
        {"email": email}
    )

    if existing_user:
        return None

    hashed_password = hash_password(password)

    user_data = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "role": role,
        "is_active": True,
    }

    result = await users_collection.insert_one(
        user_data
    )

    created_user = await users_collection.find_one(
        {"_id": result.inserted_id}
    )

    return {
        "message": "User registered successfully",
        "user": {
            "id": str(created_user["_id"]),
            "name": created_user["name"],
            "email": created_user["email"],
            "role": created_user["role"],
        },
    }


async def authenticate_user(
    users_collection,
    email: str,
    password: str,
) -> Optional[dict]:

    user = await users_collection.find_one(
        {"email": email}
    )

    if user is None:
        return None

    if user.get("is_active", True) is False:
        return None

    hashed_password = user.get("password")

    if not hashed_password:
        return None

    if not verify_password(
        password,
        hashed_password,
    ):
        return None

    token = create_access_token(
        {
            "sub": str(user["_id"]),
            "email": user.get("email"),
            "role": user.get("role"),
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "name": user.get("name"),
            "email": user.get("email"),
            "role": user.get("role"),
        },
    }