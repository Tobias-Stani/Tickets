from tests.conftest import TEST_PASSWORD
from tests.web.conftest import CSRF_PATTERN, csrf_token, login


def test_health(web):
    assert web.get("/health").json() == {"status": "ok"}


def test_anonymous_user_is_redirected_to_login(web):
    response = web.get("/", follow_redirects=False)

    assert response.headers["location"] == "/login"


def test_home_redirects_by_role(web, admin, client_user):
    login(web, client_user.email)
    assert web.get("/", follow_redirects=False).headers["location"] == "/tickets"

    web.cookies.clear()
    login(web, admin.email)
    assert web.get("/", follow_redirects=False).headers["location"] == "/admin"


def test_login_with_wrong_password_shows_error(web, client_user):
    response = login(web, client_user.email, "wrong-password")

    assert response.status_code == 401
    assert "Email o contraseña incorrectos" in response.text


def test_post_without_csrf_token_is_rejected(web, client_user):
    web.get("/login")
    data = {"email": client_user.email, "password": TEST_PASSWORD}

    assert web.post("/login", data=data).status_code == 403


def test_deactivated_user_is_logged_out_on_next_request(web, client_user, session):
    login(web, client_user.email)
    client_user.is_active = False
    session.commit()

    response = web.get("/tickets", follow_redirects=False)

    assert response.headers["location"] == "/login"


def test_logout_clears_session(web, client_user):
    login(web, client_user.email)

    web.post("/logout", data={"csrf_token": csrf_token(web)})

    assert web.get("/", follow_redirects=False).headers["location"] == "/login"


def test_client_cannot_open_admin_pages(web, client_user):
    login(web, client_user.email)

    assert web.get("/admin/users").status_code == 403


def test_csrf_pattern_is_present_in_app_layout(web, admin):
    login(web, admin.email)

    assert CSRF_PATTERN.search(web.get("/admin").text)
