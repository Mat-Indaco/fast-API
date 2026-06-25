from datetime import datetime, timezone, date
from enum import StrEnum

from sqlmodel import Field, SQLModel


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: str
    full_name: str | None = None
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    color: str = Field(default="#6366f1")
    owner_id: int = Field(foreign_key="user.id")


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str | None = None
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: Priority = Field(default=Priority.MEDIUM)
    due_date: date | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    category_id: int | None = Field(default=None, foreign_key="category.id")
    owner_id: int = Field(foreign_key="user.id")
