import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.models.user import User

async def test_create_user_success(client: AsyncClient):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword"
    }
    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "hashed_password" not in data 

async def test_create_user_duplicate_username(client: AsyncClient, session: Session):
    existing_user = User(username="existinguser", email="existing@example.com", hashed_password="hashed_pass")
    session.add(existing_user)
    session.commit()

    user_data = {
        "username": "existinguser",
        "email": "another@example.com",
        "password": "somepassword"
    }
    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

async def test_read_users_me_authenticated(client: AsyncClient, user_token: str, session: Session):
    user_data = User(username="alice", email="alice@example.com", hashed_password="hashed_pass_alice")
    session.add(user_data)
    session.commit()

    headers = {"Authorization": f"Bearer {user_token}"}
    response = await client.get("/api/v1/users/me/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"

async def test_read_users_me_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/users/me/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"