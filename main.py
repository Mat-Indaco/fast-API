import logging
import time

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import settings
from limiter import limiter
from routers.auth import router as auth_router
from routers.categories import router as categories_router
from routers.tasks import router as tasks_router
from routers.users import router as users_router
from ws import manager

# ── Logging ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── App ──────────────────────────────────────────────────────────
app = FastAPI(title="Task Manager API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(categories_router)

templates = Jinja2Templates(directory="templates")


# ── Middleware: request logging ───────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s  →  %d  (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        ms,
    )
    return response


# ── WebSocket ────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username = payload.get("sub")
        if not username:
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)
    logger.info("WS connect: %s  (total: %d)", username, manager.count)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WS disconnect: %s  (total: %d)", username, manager.count)


# ── Pages ────────────────────────────────────────────────────────
@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/home")
def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


# ── Health check ─────────────────────────────────────────────────
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
