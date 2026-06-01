from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select

from db import SessionDep
from models import Item, User
from schemas import ItemCreate, ItemRead
from security import get_current_user

router = APIRouter(prefix="/items", tags=["items"])


# ENDPOINT DE ESCRITURA
# response_model=ItemRead le dice a FastAPI qué forma tiene la respuesta.
# FastAPI la usa para: 1) generar la doc en /docs, 2) filtrar los campos
# (si tu objeto tiene campos extra, solo devuelve los de ItemRead),
# 3) validar que la respuesta es correcta.
@router.post("/", response_model=ItemRead)
def create_item(
    item: ItemCreate,               # FastAPI valida el body con este schema
    session: SessionDep,             # inyectado: sesión de base de datos
    current_user: User = Depends(get_current_user),  # inyectado: usuario logueado
):
    """Crear un nuevo item. El dueño es el usuario autenticado."""
    db_item = Item(
        title=item.title,
        description=item.description,
        owner_id=current_user.id,    # el dueño es quien está logueado
    )
    session.add(db_item)             # agregar a la sesión de DB
    session.commit()                 # guardar en la DB (hacer el INSERT)
    session.refresh(db_item)         # recargar para obtener el id generado
    return db_item


# ENDPOINT DE LECTURA
@router.get("/", response_model=list[ItemRead])
def list_items(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    offset: int = 0,                # parámetro de query: /items/?offset=10
    limit: int = Query(default=100, le=100),  # le=100 = máximo permitido
):
    """Listar items del usuario autenticado."""
    # .where() filtra: solo los items de ESTE usuario
    # .offset() salta N registros (para paginación)
    # .limit() limita la cantidad de resultados
    items = session.exec(
        select(Item)
        .where(Item.owner_id == current_user.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return items

@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Eliminar un item solo si pertenece al usuario autenticado."""

    item = session.get(Item, item_id)

    # Verificar que exista
    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    # Verificar ownership
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para eliminar este item"
        )

    session.delete(item)

    session.commit()

    return {"ok": True}