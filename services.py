from models import User
from schemas import UserCreate
from sqlmodel import Session
from fastapi import HTTPException


def fake_password_hasher(password: str):
    return "supersecret" + password


def create_user(user: UserCreate,  session: Session):

    hashed_password = fake_password_hasher(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user

def read_user(user_id:int,  session: Session):
    user = session.get(User,user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user