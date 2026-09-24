from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.core.config import get_settings
from app.core.csrf import FORM_FIELD, HEADER_NAME, get_csrf_token
from app.shared.labels import (
    format_datetime,
    role_label,
    role_options,
    status_label,
    status_options,
)
from app.shared.navigation import nav_for
from app.shared.web import pop_flash

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def current_user(request: Request):
    return getattr(request.state, "user", None)


templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.globals.update(
    app_name=get_settings().app_name,
    csrf_token=get_csrf_token,
    csrf_field=FORM_FIELD,
    csrf_header=HEADER_NAME,
    current_user=current_user,
    nav_for=nav_for,
    pop_flash=pop_flash,
    status_label=status_label,
    role_label=role_label,
    role_options=role_options,
    status_options=status_options,
)
templates.env.filters["datetime"] = format_datetime
