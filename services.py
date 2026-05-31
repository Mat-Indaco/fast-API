from models import User
from schemas import UserCreate
from sqlmodel import Session, select
from fastapi import HTTPException
from security import hash_password, verify_password


def create_user(user: UserCreate, session: Session):

    hashed_password = hash_password(user.password)

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


def read_user(user_id: int, session: Session):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def authenticate_user(username: str, password: str, session: Session):
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
