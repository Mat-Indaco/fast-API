from fastapi import FastAPI, Request

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routers.users import router as users_router
from routers.items import router as items_router
from routers.auth import router as auth_router

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
"""
REST API desarrollada con FastAPI.

Features:
- JWT 
- Roles de usuario
- CRUD de usuarios
- CRUD de items
- Docker 
- SQLite 
"""

app.include_router(users_router)
app.include_router(items_router)
app.include_router(auth_router)


templates = Jinja2Templates(directory="templates")


@app.get("/")
def login_page(request: Request):
    """Página de login."""
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/home")
def home_page(request: Request):
    """Página principal (home/dashboard)."""
    return templates.TemplateResponse(request=request, name="home.html")


@app.get("/register")
def register_page(request: Request):
    """Página de registro."""
    return templates.TemplateResponse(request=request, name="register.html")
