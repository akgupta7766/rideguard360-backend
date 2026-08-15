from pydantic import BaseModel, EmailStr


class DriverCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    license_number: str
    status: str = "active"


class DriverUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    license_number: str | None = None
    status: str | None = None


class DriverResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    license_number: str
    status: str