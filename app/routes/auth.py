from fastapi import APIRouter, Depends, HTTPException, status

from app.database.mongodb import db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.services.auth_service import (
    authenticate_user,
    register_user,
)
from app.core.security import (
    get_current_user,
    require_role,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


def get_users_collection():
    return db["users"]


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    register_data: RegisterRequest,
    users_collection=Depends(get_users_collection),
):
    result = await register_user(
        users_collection=users_collection,
        name=register_data.name,
        email=register_data.email,
        password=register_data.password,
        role=register_data.role,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    return result


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


@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user),
):
    return {
        "message": "Authenticated user",
        "user": current_user,
    }


@router.get("/admin-test")
async def admin_test(
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    return {
        "message": "Admin access granted",
        "user": current_user,
    }