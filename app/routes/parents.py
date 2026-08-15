from fastapi import APIRouter, HTTPException, status

from app.schemas.parent import (
    ParentCreate,
    ParentResponse,
    ParentUpdate,
)
from app.services.parent_service import (
    create_parent,
    get_all_parents,
    get_parent_by_id,
    update_parent,
    delete_parent,
)


router = APIRouter(
    prefix="/api/parents",
    tags=["Parents"],
)


@router.post(
    "/",
    response_model=ParentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_parent(parent_data: ParentCreate):
    result = await create_parent(
        parent_data.model_dump()
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Parent email already exists",
        )

    return result


@router.get(
    "/",
    response_model=list[ParentResponse],
)
async def get_parents():
    return await get_all_parents()


@router.get(
    "/{parent_id}",
    response_model=ParentResponse,
)
async def get_parent(parent_id: str):
    result = await get_parent_by_id(parent_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found",
        )

    return result


@router.put(
    "/{parent_id}",
    response_model=ParentResponse,
)
async def update_existing_parent(
    parent_id: str,
    parent_data: ParentUpdate,
):
    result = await update_parent(
        parent_id,
        parent_data.model_dump(exclude_none=True),
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found",
        )

    return result


@router.delete(
    "/{parent_id}",
)
async def delete_existing_parent(parent_id: str):
    result = await delete_parent(parent_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found",
        )

    return {
        "message": "Parent deleted successfully"
    }