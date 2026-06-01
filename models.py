from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from enum import StrEnum


class UserRole(StrEnum):
    """Roles disponibles en el sistema."""

    ADMIN = "admin"
    USER = "user"


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: EmailStr
    full_name: str | None = None
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)
