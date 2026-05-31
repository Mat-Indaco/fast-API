from sqlmodel import SQLModel
from pydantic import EmailStr


class Token(SQLModel):
    access_token: str
    token_type: str


class UserCreate(SQLModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    password: str


class UserRead(SQLModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None = None


class UserUpdate(SQLModel):
    username: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
