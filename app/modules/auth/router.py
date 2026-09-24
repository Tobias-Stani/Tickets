from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse, Response

from app.core.errors import AuthenticationError
from app.core.templates import templates
from app.modules.auth.dependencies import SESSION_USER_KEY, CurrentUser, DbSession
from app.modules.auth.service import AuthService

router = APIRouter(tags=["auth"])


@router.get("/login")
def login_page(request: Request) -> Response:
    if request.session.get(SESSION_USER_KEY):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request, "auth/login.html")


@router.post("/login")
def login(
    request: Request,
    db: DbSession,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
) -> Response:
    try:
        user = AuthService(db).authenticate(email, password)
    except AuthenticationError as error:
        context = {"error": error.message, "email": email}
        return templates.TemplateResponse(request, "auth/login.html", context, status_code=401)
    request.session.clear()  # fresh session on login
    request.session[SESSION_USER_KEY] = user.id
    return RedirectResponse("/", status_code=303)


@router.post("/logout")
def logout(request: Request) -> Response:
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@router.get("/")
def home(user: CurrentUser) -> Response:
    return RedirectResponse("/admin" if user.is_admin else "/tickets", status_code=303)
