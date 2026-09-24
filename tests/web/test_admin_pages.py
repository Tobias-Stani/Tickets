import pytest

from app.models import Tag, User
from tests.web.conftest import login


@pytest.fixture
def as_admin(web, admin):
    login(web, admin.email)
    return web


@pytest.mark.parametrize(
    "path",
    [
        "/admin",
        "/admin/tickets",
        "/admin/users",
        "/admin/users/new",
        "/admin/tags",
        "/admin/topics",
    ],
)
def test_admin_pages_render(as_admin, path):
    response = as_admin.get(path)

    assert response.status_code == 200
    assert "Usuarios" in response.text  # navigation menu is present


def test_dashboard_links_status_cards_to_filtered_tickets(as_admin):
    assert 'href="/admin/tickets?status=OPEN"' in as_admin.get("/admin").text


def test_create_user_with_tags_redirects_with_flash(as_admin, htmx_post, session):
    tag = Tag(name="Pro")
    session.add(tag)
    session.commit()
    data = {
        "full_name": "Ana",
        "email": "ana@x.com",
        "password": "12345678",
        "role": "CLIENT",
        "tag_ids": [str(tag.id)],
    }

    response = htmx_post("/admin/users", data=data)

    assert response.headers["HX-Redirect"] == "/admin/users"
    user = session.query(User).filter_by(email="ana@x.com").one()
    assert [t.name for t in user.tags] == ["Pro"]
    assert "Usuario Ana creado." in as_admin.get("/admin/users").text


def test_invalid_form_returns_spanish_alert(as_admin, htmx_post):
    data = {"full_name": "Ana", "email": "ana@x.com", "password": "123", "role": "CLIENT"}

    response = htmx_post("/admin/users", data=data)

    assert response.status_code == 422
    assert "Contraseña debe tener al menos 8 caracteres" in response.text


def test_duplicate_tag_returns_conflict_alert(as_admin, htmx_post):
    htmx_post("/admin/tags", data={"name": "Pro", "color": "#10b981"})

    response = htmx_post("/admin/tags", data={"name": "pro", "color": "#10b981"})

    assert response.status_code == 409
    assert "Ya existe una etiqueta" in response.text


def test_toggle_user_active(as_admin, htmx_post, client_user, session):
    htmx_post(f"/admin/users/{client_user.id}/active", data={"is_active": "false"})

    session.refresh(client_user)
    assert not client_user.is_active
