from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from enum import StrEnum


class Item(SQLModel, table=True):
    """Modelo de item en la base de datos."""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str | None = None
    cant: int = Field(default=1)
    owner_id: int = Field(foreign_key="user.id")


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
