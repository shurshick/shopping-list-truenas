from .conftest import login, register_user, setup_admin


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_health_endpoint_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_registration_forbidden_before_setup(client):
    response = client.post("/auth/register", json={"email": "user@example.com", "password": "secret123"})

    assert response.status_code == 403


def test_setup_requires_csrf_token(client):
    response = client.post(
        "/setup",
        data={
            "admin_email": "admin@example.com",
            "admin_password": "adminpass123",
            "admin_password_confirm": "adminpass123",
            "app_name": "Список покупок",
            "external_url": "https://shopping.example.com",
            "allow_registration": "true",
        },
    )

    assert response.status_code == 422


def test_setup_rejects_invalid_csrf_token(client):
    response = client.post(
        "/setup",
        data={
            "csrf_token": "invalid-token",
            "admin_email": "admin@example.com",
            "admin_password": "adminpass123",
            "admin_password_confirm": "adminpass123",
            "app_name": "Список покупок",
            "external_url": "https://shopping.example.com",
            "allow_registration": "true",
        },
        headers={"origin": "http://testserver"},
    )

    assert response.status_code == 403


def test_setup_creates_first_admin(client):
    token = setup_admin(client)

    response = client.get("/admin/status", headers=auth(token))
    assert response.status_code == 200
    assert response.json()["setup_completed"] is True


def test_wrong_password_returns_401(client):
    setup_admin(client)

    response = client.post("/auth/login", json={"email": "admin@example.com", "password": "wrongpass"})

    assert response.status_code == 401


def test_login_rate_limit_returns_429(client):
    setup_admin(client)

    for _ in range(10):
        response = client.post("/auth/login", json={"email": "limited@example.com", "password": "wrongpass"})
        assert response.status_code == 401
    response = client.post("/auth/login", json={"email": "limited@example.com", "password": "wrongpass"})

    assert response.status_code == 429


def test_non_admin_cannot_access_admin_status(client):
    setup_admin(client)
    user_token = register_user(client, "user@example.com")

    response = client.get("/admin/status", headers=auth(user_token))

    assert response.status_code == 403


def test_user_cannot_access_another_users_list(client):
    admin_token = setup_admin(client)
    create_response = client.post("/lists", json={"name": "private"}, headers=auth(admin_token))
    list_id = create_response.json()["id"]
    user_token = register_user(client, "guest@example.com")

    response = client.patch("/lists/{list_id}".format(list_id=list_id), json={"name": "stolen"}, headers=auth(user_token))

    assert response.status_code == 404


def test_invite_cannot_be_accepted_twice(client):
    admin_token = setup_admin(client)
    create_response = client.post("/lists", json={"name": "shared"}, headers=auth(admin_token))
    list_id = create_response.json()["id"]
    invite = client.post(f"/lists/{list_id}/invite", headers=auth(admin_token)).json()
    user_one_token = register_user(client, "one@example.com")
    user_two_token = register_user(client, "two@example.com")

    first = client.post(f"/invites/{invite['token']}/accept", headers=auth(user_one_token))
    second = client.post(f"/invites/{invite['token']}/accept", headers=auth(user_two_token))

    assert first.status_code == 200
    assert second.status_code == 404


def test_server_config_does_not_expose_secrets(client):
    setup_admin(client)

    response = client.get("/server-config")
    body = response.text.lower()

    assert response.status_code == 200
    assert "jwt_secret" not in body
    assert "postgres_password" not in body
    assert "database_url" not in body
