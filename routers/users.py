from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Annotated
from db import SessionDep
from sqlalchemy import func
from schemas import UserCreate, UserRead, UserUpdate
from services import create_user, read_user
from sqlmodel import select
from models import User,Item
from security import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def create_new_user(user: UserCreate, session: SessionDep):
    """
    Crear un nuevo usuario en el sistema.

    El endpoint recibe username, email y password.
    También permite asignar un rol (user/admin).

    Devuelve la información pública del usuario creado.
    """

    existing_username = session.exec(
        select(User).where(User.username == user.username)
    ).first()

    if existing_username:
        raise HTTPException(status_code=409, detail="Username already exists")

    existing_email = session.exec(select(User).where(User.email == user.email)).first()

    if existing_email:
        raise HTTPException(status_code=409, detail="Email already exists")
    db_user = create_user(user, session)

    return db_user


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int, session: SessionDep, current_user: User = Depends(get_current_user)
):
    """
    Obtiene la información de un usuario específico.

    Requiere autenticación mediante JWT.
    """

    db_user = read_user(user_id, session)

    return db_user


@router.get("/", response_model=list[UserRead])
def read_users(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    """
    Devuelve una lista paginada de usuarios registrados.

    Requiere autenticación.

    Parámetros:
    - offset: cantidad de registros a omitir
    - limit: cantidad máxima de resultados
    """
    users = session.exec(select(User).offset(offset).limit(limit)).all()

    return users


@router.delete("/{user_id}")
def delete_user(
    user_id: int, session: SessionDep, current_user: User = Depends(require_admin)
):
    """
    Elimina un usuario de la base de datos.

    Solo los administradores pueden realizar esta acción.

    Restricciones:
    - Un administrador no puede eliminarse a sí mismo.
    """

    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}

@router.get("/{user_id}/items/count")
def count_user_items(
    user_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """
    Devuelve la cantidad de items que tiene un usuario.

    Requiere autenticación JWT.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    count = session.exec(select(func.count()).where(Item.owner_id == user_id)).one()

    return {"user_id": user_id, "username": user.username, "item_count": count}


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_update: UserUpdate, session: SessionDep):
    """
    Actualiza parcialmente la información de un usuario.

    Solo se modifican los campos enviados en el request.
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user_update.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


