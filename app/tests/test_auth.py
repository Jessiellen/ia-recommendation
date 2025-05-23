import pytest
from httpx import AsyncClient
from app.auth.jwks import verify_password
from app.models.user import User # Importe seu modelo de usuário

async def test_login_success(client: AsyncClient, session: Session):
    hashed_password = "password_hash_for_test"
    

    user_data = User(username="testuser", email="test@example.com", hashed_password="password_hash_for_test")
    session.add(user_data)
    session.commit()

    response = await client.post(
        "/api/v1/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/v1/token",
        data={"username": "nonexistent", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"

async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/token",
        data={"username": "anotheruser", "password": "anypassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"

async def test_login_wrong_password(client: AsyncClient, session: Session):
    user_data = User(username="userwithpass", email="user@example.com", hashed_password="password_hash_for_test")
    session.add(user_data)
    session.commit()

    response = await client.post(
        "/api/v1/token",
        data={"username": "userwithpass", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"