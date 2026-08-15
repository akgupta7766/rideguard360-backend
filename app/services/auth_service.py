from typing import Optional

from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(
    users_collection,
    email: str,
    password: str,
) -> Optional[dict]:
    user = await users_collection.find_one({"email": email})

    if user is None:
        return None

    hashed_password = user.get("password")

    if not hashed_password:
        return None

    if not verify_password(password, hashed_password):
        return None

    return {
        "message": "Login successful",
        "user": {
            "id": str(user["_id"]),
            "name": user.get("name"),
            "email": user.get("email"),
            "role": user.get("role"),
        },
    }