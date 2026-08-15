from pydantic import BaseModel, EmailStr


class ParentCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    student_ids: list[str] = []
    status: str = "active"


class ParentUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    student_ids: list[str] | None = None
    status: str | None = None


class ParentResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    student_ids: list[str] = []
    status: str