from typing import Annotated

from fastapi import Depends, Query, Request
from fastapi.responses import RedirectResponse, Response

from app.shared.pagination import PageParams

FLASH_KEY = "flash"


def flash(request: Request, message: str, kind: str = "success") -> None:
    request.session[FLASH_KEY] = {"message": message, "kind": kind}


def pop_flash(request: Request) -> dict | None:
    return request.session.pop(FLASH_KEY, None)


def is_htmx(request: Request) -> bool:
    return request.headers.get("HX-Request") == "true"


def redirect(request: Request, url: str, message: str | None = None) -> Response:
    """Post/Redirect/Get that works for both HTMX and plain form submissions."""
    if message:
        flash(request, message)
    if is_htmx(request):
        return Response(status_code=204, headers={"HX-Redirect": url})
    return RedirectResponse(url, status_code=303)


def optional_int(value: str | None) -> int | None:
    """Query/form selects send "" for "all"; treat it as no filter."""
    return int(value) if value and value.isdigit() else None


def get_page_params(page: Annotated[int, Query(ge=1)] = 1) -> PageParams:
    return PageParams(page=page)


Pagination = Annotated[PageParams, Depends(get_page_params)]
