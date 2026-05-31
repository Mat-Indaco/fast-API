from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import create_db_and_tables

from routers.users import router as users_router
from routers.items import router as items_router
from routers.auth import router as auth_router

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(users_router)
app.include_router(items_router)
app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"message": "API funcionando"}
