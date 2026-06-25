from datetime import datetime, date

from pydantic import EmailStr
from sqlmodel import SQLModel

from models import Priority, TaskStatus, UserRole


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenPair(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(SQLModel):
    refresh_token: str


class TokenData(SQLModel):
    username: str | None = None


class UserBase(SQLModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class UserUpdate(SQLModel):
    username: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    role: UserRole | None = None


class CategoryBase(SQLModel):
    name: str
    color: str = "#6366f1"


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    owner_id: int


class TaskBase(SQLModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    due_date: date | None = None
    category_id: int | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: Priority | None = None
    due_date: date | None = None
    category_id: int | None = None


class TaskRead(TaskBase):
    id: int
    owner_id: int
    created_at: datetime


class TaskStats(SQLModel):
    total: int
    pending: int
    in_progress: int
    done: int
    overdue: int
