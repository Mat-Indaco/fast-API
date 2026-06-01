from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from db import create_db_and_tables

from fastapi.templating import Jinja2Templates

from routers.users import router as users_router
from routers.items import router as items_router
from routers.auth import router as auth_router

app = FastAPI()


#@asynccontextmanager
#async def lifespan(app: FastAPI):
#    create_db_and_tables()
#    yield


#app = FastAPI(lifespan=lifespan)


app.include_router(users_router)
app.include_router(items_router)
app.include_router(auth_router)


templates = Jinja2Templates(directory="templates")


@app.get("/")
def login_page(request: Request):
    """Página de login."""
    return templates.TemplateResponse(request=request, name="login.html")


# Agregar esta ruta nueva:
@app.get("/home")
def home_page(request: Request):
    """Página principal (home/dashboard)."""
    return templates.TemplateResponse(request=request, name="home.html")


# @app.get("/")
# def read_root():
#    return {"message": "API funcionando"}
