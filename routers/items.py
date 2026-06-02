from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select

from db import SessionDep
from models import Item, User
from schemas import ItemCreate, ItemRead
from security import get_current_user

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemRead)
def create_item(
    item: ItemCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """
    Crea un nuevo item asociado al usuario autenticado.

    El owner del item se asigna automáticamente
    a partir del token JWT.
    """

    existing_item = session.exec(
        select(Item).where(Item.title == item.title, Item.owner_id == current_user.id)
    ).first()

    if existing_item:
        existing_item.cant += item.cant

        session.add(existing_item)

        session.commit()

        session.refresh(existing_item)

        return existing_item

    db_item = Item(
        title=item.title,
        description=item.description,
        cant=item.cant,
        owner_id=current_user.id,
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("/", response_model=list[ItemRead])
def list_items(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    """
    Devuelve los items pertenecientes al usuario autenticado.

    Incluye soporte de paginación mediante:
    - offset
    - limit
    """

    items = session.exec(
        select(Item).where(Item.owner_id == current_user.id).offset(offset).limit(limit)
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

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="No tienes permisos para eliminar este item"
        )

    session.delete(item)

    session.commit()

    return {"ok": True}
