from sqlmodel import SQLModel
from pydantic import EmailStr
from models import UserRole


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None


class UserCreate(SQLModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    password: str
    role: UserRole = UserRole.USER


class UserRead(SQLModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None = None
    role: UserRole


class UserUpdate(SQLModel):
    username: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    role: UserRole | None = None
