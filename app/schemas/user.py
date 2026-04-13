from app.models.user import UserBase
from sqlmodel import SQLModel
from pydantic import EmailStr
from typing import Optional


class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    monthly_income: Optional[float] = None


class AdminCreate(UserBase):
    role: str = "admin"


class RegularUserCreate(UserBase):
    role: str = "regular_user"


class UserResponse(SQLModel):
    id: int
    username: str
    email: EmailStr
    monthly_income: float


class SignupRequest(SQLModel):
    username: str
    email: EmailStr
    password: str
