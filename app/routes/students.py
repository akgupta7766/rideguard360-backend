from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_role
from app.schemas.student import (
    StudentCreate,
    StudentResponse,
    StudentUpdate,
)
from app.services.student_service import (
    create_student,
    get_all_students,
    get_student_by_id,
    update_student,
    delete_student,
)


router = APIRouter(
    prefix="/api/students",
    tags=["Students"],
)


@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_student(
    student_data: StudentCreate,
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    result = await create_student(
        student_data.model_dump()
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student email or student ID already exists",
        )

    return result


@router.get(
    "/",
    response_model=list[StudentResponse],
)
async def get_students(
    current_user: dict = Depends(
        require_role("admin", "driver", "parent")
    ),
):
    return await get_all_students()


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
)
async def get_student(
    student_id: str,
    current_user: dict = Depends(
        require_role("admin", "driver", "parent")
    ),
):
    result = await get_student_by_id(student_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return result


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
)
async def update_existing_student(
    student_id: str,
    student_data: StudentUpdate,
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    result = await update_student(
        student_id,
        student_data.model_dump(exclude_none=True),
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return result


@router.delete(
    "/{student_id}",
)
async def delete_existing_student(
    student_id: str,
    current_user: dict = Depends(
        require_role("admin")
    ),
):
    result = await delete_student(student_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return {
        "message": "Student deleted successfully"
    }