from datetime import date, datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select

from db import SessionDep
from models import Priority, Task, TaskStatus, User
from schemas import TaskCreate, TaskRead, TaskStats, TaskUpdate
from security import get_current_user
from ws import manager

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskRead, status_code=201)
async def create_task(
    task: TaskCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    db_task = Task(**task.model_dump(), owner_id=current_user.id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    await manager.broadcast({
        "event": "task_created",
        "task_id": db_task.id,
        "title": db_task.title,
        "username": current_user.username,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    return db_task


@router.get("/stats", response_model=TaskStats)
def get_task_stats(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    tasks = session.exec(
        select(Task).where(Task.owner_id == current_user.id)
    ).all()
    today = date.today()
    return TaskStats(
        total=len(tasks),
        pending=sum(1 for t in tasks if t.status == TaskStatus.PENDING),
        in_progress=sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS),
        done=sum(1 for t in tasks if t.status == TaskStatus.DONE),
        overdue=sum(
            1 for t in tasks
            if t.due_date and t.due_date < today and t.status != TaskStatus.DONE
        ),
    )


@router.get("/", response_model=list[TaskRead])
def list_tasks(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    status: TaskStatus | None = None,
    priority: Priority | None = None,
    category_id: int | None = None,
    search: str | None = Query(default=None),
    sort_by: Literal["created_at", "due_date", "priority"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
    offset: int = 0,
    limit: int = Query(default=50, le=100),
):
    statement = select(Task).where(Task.owner_id == current_user.id)
    if status:
        statement = statement.where(Task.status == status)
    if priority:
        statement = statement.where(Task.priority == priority)
    if category_id is not None:
        statement = statement.where(Task.category_id == category_id)
    if search:
        statement = statement.where(Task.title.ilike(f"%{search}%"))

    priority_order = {"low": 0, "medium": 1, "high": 2}
    tasks = session.exec(statement.offset(offset).limit(limit)).all()

    if sort_by == "priority":
        tasks = sorted(tasks, key=lambda t: priority_order.get(t.priority, 0), reverse=(order == "desc"))
    elif sort_by == "due_date":
        tasks = sorted(tasks, key=lambda t: (t.due_date is None, t.due_date), reverse=(order == "desc"))
    else:
        tasks = sorted(tasks, key=lambda t: t.created_at, reverse=(order == "desc"))

    return tasks


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    changes = task_update.model_dump(exclude_unset=True)
    task.sqlmodel_update(changes)
    session.add(task)
    session.commit()
    session.refresh(task)

    await manager.broadcast({
        "event": "task_updated",
        "task_id": task.id,
        "title": task.title,
        "status": task.status,
        "username": current_user.username,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    title = task.title
    session.delete(task)
    session.commit()

    await manager.broadcast({
        "event": "task_deleted",
        "task_id": task_id,
        "title": title,
        "username": current_user.username,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    return {"ok": True}
