import re
from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import create_app
from tests.conftest import TEST_PASSWORD

CSRF_PATTERN = re.compile(r'name="csrf_token" value="([^"]+)"')


@pytest.fixture
def web(session_factory) -> TestClient:
    app = create_app()

    def override_db():
        with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def csrf_token(web: TestClient) -> str:
    """Every page (login or app layout) renders a form carrying the session token."""
    return CSRF_PATTERN.search(web.get("/").text).group(1)


def login(web: TestClient, email: str, password: str = TEST_PASSWORD):
    data = {"email": email, "password": password, "csrf_token": csrf_token(web)}
    return web.post("/login", data=data, follow_redirects=False)


@pytest.fixture
def htmx_post(web) -> Callable:
    """Posts like HTMX does: CSRF header + HX-Request, without following redirects."""

    def post(url: str, **kwargs):
        headers = {"HX-Request": "true", "X-CSRF-Token": csrf_token(web)}
        return web.post(url, headers=headers, follow_redirects=False, **kwargs)

    return post
