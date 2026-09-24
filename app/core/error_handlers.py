from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse, Response

from app.core.errors import DomainError
from app.core.templates import templates
from app.core.validation_messages import describe
from app.modules.auth.dependencies import NotAuthenticatedError
from app.shared.web import is_htmx

LOGIN_URL = "/login"


def _render_error(request: Request, message: str, status_code: int) -> Response:
    """HTMX requests get an inline alert fragment; full page loads get the error page."""
    template = "components/alert_fragment.html" if is_htmx(request) else "errors/error.html"
    return templates.TemplateResponse(
        request, template, {"message": message}, status_code=status_code
    )


async def handle_not_authenticated(request: Request, _: NotAuthenticatedError) -> Response:
    if is_htmx(request):
        return Response(status_code=204, headers={"HX-Redirect": LOGIN_URL})
    return RedirectResponse(LOGIN_URL, status_code=303)


async def handle_domain_error(request: Request, error: DomainError) -> Response:
    return _render_error(request, error.message, error.status_code)


async def handle_validation_error(request: Request, error: RequestValidationError) -> Response:
    return _render_error(request, describe(list(error.errors())), 422)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotAuthenticatedError, handle_not_authenticated)
    app.add_exception_handler(DomainError, handle_domain_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
