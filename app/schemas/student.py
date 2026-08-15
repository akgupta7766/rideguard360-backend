from pydantic import BaseModel, EmailStr


class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    student_id: str
    grade: str
    section: str
    parent_id: str | None = None
    status: str = "active"


class StudentUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    student_id: str | None = None
    grade: str | None = None
    section: str | None = None
    parent_id: str | None = None
    status: str | None = None


class StudentResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    student_id: str
    grade: str
    section: str
    parent_id: str | None = None
    status: str