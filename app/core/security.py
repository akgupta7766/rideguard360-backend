from datetime import datetime, timedelta, timezone
import os
import secrets

from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext


load_dotenv()


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "development-secret-change-this",
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "60",
    )
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    data: dict,
    expires_minutes: int | None = None,
) -> str:
    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload.update({"exp": expire})

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return payload

    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
) -> dict:

    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    user_id = payload.get("sub")
    email = payload.get("email")
    role = payload.get("role")

    if not user_id or not email or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    return {
        "id": user_id,
        "email": email,
        "role": role,
    }

def require_role(*allowed_roles: str):
    async def role_checker(
        current_user: dict = Depends(get_current_user),
    ) -> dict:

        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

        return current_user

    return role_checker


async def require_gps_update_access(
    simulator_key: str | None = Header(
        default=None,
        alias="X-GPS-Simulator-Key",
    ),
    credentials: HTTPAuthorizationCredentials | None = Depends(
        optional_security
    ),
) -> dict:
    """Allow a simulator API key or an existing admin/driver JWT."""
    expected_key = os.getenv("GPS_SIMULATOR_API_KEY")

    if (
        expected_key
        and simulator_key
        and secrets.compare_digest(simulator_key, expected_key)
    ):
        return {"id": "gps-simulator", "role": "simulator"}

    if credentials:
        payload = decode_access_token(credentials.credentials)
        if payload and payload.get("role") in {"admin", "driver"}:
            return {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload["role"],
            }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Valid simulator key or admin/driver token required",
    )
