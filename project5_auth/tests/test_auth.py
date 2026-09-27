import pytest

from app import create_app, db


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        TESTING=True,
    )
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_register_and_login(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "a@b.com", "username": "alice", "password": "Str0ng!Pass"},
    )
    assert resp.status_code == 201

    resp = client.post(
        "/api/auth/login", json={"email": "a@b.com", "password": "Str0ng!Pass"}
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"email": "c@d.com", "username": "bob", "password": "Str0ng!Pass"},
    )
    resp = client.post(
        "/api/auth/login", json={"email": "c@d.com", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_protected_route_requires_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_weak_password_rejected(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "e@f.com", "username": "carol", "password": "weak"},
    )
    assert resp.status_code == 400
