from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

from security import create_access_token
from db import SessionDep
from schemas import Token
from services import authenticate_user
router = APIRouter( tags=["auth"])



@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: SessionDep = None
):

    user = authenticate_user(
        form_data.username,
        form_data.password,
        session
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(
        data={"sub": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }