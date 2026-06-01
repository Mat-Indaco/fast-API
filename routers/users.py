from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Annotated
from db import SessionDep
from schemas import UserCreate, UserRead, UserUpdate
from services import create_user, read_user
from sqlmodel import select
from models import User
from security import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def create_new_user(user: UserCreate, session: SessionDep):

    db_user = create_user(user, session)

    return db_user


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int, session: SessionDep, current_user: User = Depends(get_current_user)
):

    db_user = read_user(user_id, session)

    return db_user


@router.get("/", response_model=list[UserRead])
def read_users(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):

    users = session.exec(select(User).offset(offset).limit(limit)).all()

    return users


@router.delete("/{user_id}")
def delete_user(
    user_id: int, session: SessionDep, current_user: User = Depends(require_admin)
):
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400,
            detail="No puedes eliminarte a ti mismo"
        )
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_update: UserUpdate, session: SessionDep):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user_update.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
