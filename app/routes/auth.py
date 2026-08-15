from fastapi import APIRouter, Depends, HTTPException, status

from app.database.mongodb import db
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import authenticate_user


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


def get_users_collection():
    return db["users"]


@router.post(
    "/login",
    response_model=LoginResponse,
)
async def login(
    login_data: LoginRequest,
    users_collection=Depends(get_users_collection),
):
    result = await authenticate_user(
        users_collection=users_collection,
        email=login_data.email,
        password=login_data.password,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return result