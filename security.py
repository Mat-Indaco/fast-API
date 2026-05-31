from datetime import datetime, timedelta, timezone
from typing import Annotated
from models import User
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from pwdlib import PasswordHash
import jwt

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
password_hash = PasswordHash.recommended()

def hash_password(password: str):
    return password_hash.hash(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def decode_token(token):
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = decode_token(token)
    return user

def verify_password(plain_pw,hashed_pw):
    return password_hash.verify(plain_pw,hashed_pw)

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


