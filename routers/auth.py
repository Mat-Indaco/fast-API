from fastapi import APIRouter, Depends, HTTPException, Request

from limiter import limiter
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from db import get_session
from models import User
from schemas import RefreshRequest, TokenPair
from security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from services import authenticate_user

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=TokenPair)
@limiter.limit("10/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """Login con username y password. Devuelve access + refresh token."""
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token_data = {"sub": user.username, "role": user.role}
    return TokenPair(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.post("/refresh", response_model=TokenPair)
@limiter.limit("10/minute")
def refresh(
    request: Request,
    body: RefreshRequest,
    session: Session = Depends(get_session),
):
    """Genera un nuevo par de tokens usando un refresh token válido."""
    username = decode_refresh_token(body.refresh_token)

    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    token_data = {"sub": user.username, "role": user.role}
    return TokenPair(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )
