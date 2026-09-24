import secrets

from fastapi import Request

from app.core.errors import PermissionDeniedError

SESSION_KEY = "csrf_token"
HEADER_NAME = "X-CSRF-Token"
FORM_FIELD = "csrf_token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def get_csrf_token(request: Request) -> str:
    token = request.session.get(SESSION_KEY)
    if token is None:
        token = secrets.token_urlsafe(32)
        request.session[SESSION_KEY] = token
    return token


async def verify_csrf(request: Request) -> None:
    """Global dependency: every state-changing request must echo the session token.

    HTMX sends it as a header (set once on <body>); plain forms as a hidden field.
    """
    if request.method in SAFE_METHODS:
        return
    expected = request.session.get(SESSION_KEY)
    sent = request.headers.get(HEADER_NAME) or await _form_token(request)
    if not expected or not sent or not secrets.compare_digest(expected, sent):
        raise PermissionDeniedError("Tu sesión expiró. Recarga la página.")


async def _form_token(request: Request) -> str | None:
    form = await request.form()
    token = form.get(FORM_FIELD)
    return token if isinstance(token, str) else None
