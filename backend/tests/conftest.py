import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


TEST_DB = Path(__file__).with_name("test.sqlite3")
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["JWT_SECRET"] = "test-secret-for-pytest"

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.rate_limit import reset_rate_limits  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    reset_rate_limits()
    with TestClient(app) as test_client:
        yield test_client
    reset_rate_limits()


def setup_admin(client: TestClient, email: str = "admin@example.com", password: str = "adminpass123") -> str:
    page = client.get("/setup")
    csrf_token = page.text.split('name="csrf_token" value="', 1)[1].split('"', 1)[0]
    response = client.post(
        "/setup",
        data={
            "csrf_token": csrf_token,
            "admin_email": email,
            "admin_password": password,
            "admin_password_confirm": password,
            "app_name": "Список покупок",
            "external_url": "https://shopping.example.com",
            "allow_registration": "true",
        },
        headers={"origin": "http://testserver"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    return login(client, email, password)


def login(client: TestClient, email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def register_user(client: TestClient, email: str, password: str = "userpass123") -> str:
    response = client.post("/auth/register", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]
