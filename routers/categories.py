from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from db import SessionDep
from models import Category, Task, User
from schemas import CategoryCreate, CategoryRead
from security import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryRead, status_code=201)
def create_category(
    category: CategoryCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    existing = session.exec(
        select(Category).where(
            Category.name == category.name,
            Category.owner_id == current_user.id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre")

    db_cat = Category(**category.model_dump(), owner_id=current_user.id)
    session.add(db_cat)
    session.commit()
    session.refresh(db_cat)
    return db_cat


@router.get("/", response_model=list[CategoryRead])
def list_categories(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    return session.exec(
        select(Category).where(Category.owner_id == current_user.id)
    ).all()


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if category.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    # Desasociar tareas de esta categoría antes de eliminarla
    tasks = session.exec(
        select(Task).where(Task.category_id == category_id)
    ).all()
    for task in tasks:
        task.category_id = None
        session.add(task)

    session.delete(category)
    session.commit()
    return {"ok": True}
