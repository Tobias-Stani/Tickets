from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import get_settings
from app.core.csrf import verify_csrf
from app.core.error_handlers import register_error_handlers
from app.modules.auth.router import router as auth_router
from app.modules.tags.router import router as tags_router
from app.modules.tickets.admin_router import router as tickets_admin_router
from app.modules.tickets.router import router as tickets_router
from app.modules.topics.router import router as topics_router
from app.modules.users.router import router as users_router

STATIC_DIR = Path(__file__).resolve().parent / "static"
ROUTERS = (
    auth_router,
    tickets_router,
    tickets_admin_router,
    users_router,
    tags_router,
    topics_router,
)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        docs_url=None,
        redoc_url=None,
        dependencies=[Depends(verify_csrf)],
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        max_age=settings.session_max_age_seconds,
        https_only=settings.https_only_cookies,
        same_site="lax",
    )
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    for router in ROUTERS:
        app.include_router(router)
    app.add_api_route("/health", lambda: {"status": "ok"}, include_in_schema=False)
    register_error_handlers(app)
    return app


app = create_app()
