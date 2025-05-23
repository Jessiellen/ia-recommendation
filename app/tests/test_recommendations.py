import pytest
from fastapi.testclient import TestClient 
from sqlalchemy.orm import Session
from app.models.user import User

async def test_get_recommendations_success_with_mock(
    client: TestClient, user_token: str, mock_recommendation_agent, db_session: Session
):
    from app.auth.jwks import get_password_hash
    user_data = User(username="alice", email="alice@example.com", hashed_password=get_password_hash("alicepassword"))
    db_session.add(user_data)
    db_session.commit()

    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/api/v1/recommendations/", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2 
    assert data[0]["product_id"] == 991
    assert data[1]["product_name"] == "Mocked Headphones"

    
    mock_recommendation_agent.generate_recommendations.assert_called_once_with(user_data.username)


async def test_get_recommendations_unauthenticated(client: TestClient):
    response = client.get("/api/v1/recommendations/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

async def test_get_recommendations_invalid_token(client: TestClient):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/recommendations/", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

async def test_get_recommendations_fallback_scenario(
    client: TestClient, user_token: str, mock_recommendation_agent, db_session: Session
):
    from app.auth.jwks import get_password_hash
    user_data = User(username="alice", email="alice@example.com", hashed_password=get_password_hash("alicepassword"))
    db_session.add(user_data)
    db_session.commit()

    mock_recommendation_agent.generate_recommendations.side_effect = Exception("Simulated LLM failure")

    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/api/v1/recommendations/", headers=headers)

    assert response.status_code == 200 
    data = response.json()

    expected_fallback_data = [
        {"product_id": 901, "product_name": "Livro Bestseller de Ficção", "reason": "Um dos livros mais vendidos no momento, elogiado pela crítica e leitores."},
        {"product_id": 902, "product_name": "Fone de Ouvido Sem Fio (Cancelamento de Ruído)", "reason": "Ideal para trabalho remoto ou viagens, proporcionando imersão total."},
        {"product_id": 903, "product_name": "Planta Decorativa para Casa (Fácil Cuidado)", "reason": "Adiciona um toque de natureza ao ambiente e melhora a qualidade do ar, requerendo pouca manutenção."}
    ]
    assert data == expected_fallback_data

    mock_recommendation_agent.generate_recommendations.assert_called_once_with(user_data.username)