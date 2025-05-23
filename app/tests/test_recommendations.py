# app/tests/test_recommendations.py
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, create_tables, drop_tables, SessionLocal
from app.models import User as UserModel, Product as ProductModel
from app.core.security import get_password_hash
from app.schemas import User, Recommendation # Importe os schemas necessários

# Fixtures do conftest.py (assumindo que já estão configuradas lá)
# @pytest.fixture(scope="session")
# def setup_test_database(): ...
# @pytest.fixture
# def db_session(setup_test_database): ...
# @pytest.fixture
# def client(): ...


@pytest.fixture
def mock_ollama_llm():
    with patch('app.agents.recommendation_agent.Ollama') as mock_ollama_class:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = """
        Product ID: 101, Name: Smartwatch X2, Reason: Ótimo para monitoramento de saúde e notificações.
        Product ID: 102, Name: Fone Bluetooth Pro, Reason: Qualidade de áudio superior e confortável.
        Product ID: 103, Name: E-reader Lumina, Reason: Ideal para leitura digital com tela confortável.
        """
        mock_ollama_class.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def test_user_and_token(client, db_session):
    drop_tables()
    create_tables()

    user_data = {"username": "testuser", "email": "test@example.com", "password": "testpassword"}
    hashed_password = get_password_hash(user_data["password"])
    db_user = UserModel(username=user_data["username"], email=user_data["email"], hashed_password=hashed_password)
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)

    product1 = ProductModel(name="Teclado Mecânico", description="Teclado com switches azuis", user_id=db_user.id)
    product2 = ProductModel(name="Mouse Gamer RGB", description="Mouse com alta precisão", user_id=db_user.id)
    db_session.add_all([product1, product2])
    db_session.commit()
    db_session.refresh(product1)
    db_session.refresh(product2)


    login_data = {"username": user_data["username"], "password": user_data["password"]}
    token_response = client.post("/api/v1/token", data=login_data)
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    return db_user, token


def test_create_user(client, db_session):
    """Testa a criação de um novo usuário."""
    user_data = {"username": "newuser", "email": "new@example.com", "password": "securepassword"}
    response = client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 200
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "new@example.com"
    assert "hashed_password" not in response.json() # Não deve retornar o hash da senha

    db_user = db_session.query(UserModel).filter(UserModel.username == "newuser").first()
    assert db_user is not None
    assert db_user.email == "new@example.com"

def test_login_for_access_token(client, test_user_and_token):
    """Testa o endpoint de login para obter um token."""
    user_model, token = test_user_and_token

    assert token is not None
    assert isinstance(token, str)

    response_fail = client.post("/api/v1/token", data={"username": "wronguser", "password": "wrongpassword"})
    assert response_fail.status_code == 401
    assert response_fail.json()["detail"] == "Incorrect username or password"

def test_read_users_me(client, test_user_and_token):
    """Testa o endpoint de usuário logado."""
    user_model, token = test_user_and_token

    response = client.get(
        "/api/v1/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == user_model.username
    assert response.json()["email"] == user_model.email

    response_no_auth = client.get("/api/v1/users/me/")
    assert response_no_auth.status_code == 401

@pytest.mark.asyncio
async def test_generate_recommendations_with_mock(client, db_session, test_user_and_token, mock_ollama_llm):
    """
    Testa o endpoint de recomendações usando o mock do Ollama LLM.
    Verifica a integração do FastAPI com o agente CrewAI mockado e o histórico de produtos.
    """
    user_model, token = test_user_and_token

    response = client.get(
        "/api/v1/recommendations/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    recommendations = response.json()
    assert len(recommendations) == 3 # Esperamos 3 recomendações

    for rec in recommendations:
        assert "product_id" in rec
        assert "product_name" in rec
        assert "reason" in rec
        assert isinstance(rec["product_id"], int)
        assert isinstance(rec["product_name"], str)
        assert isinstance(rec["reason"], str)

    mock_ollama_llm.invoke.assert_called_once() # Garante que a LLM foi chamada

# teste de integração real (pode ser útil, mas não é para CI/CD)
# @pytest.mark.integration
# def test_ollama_real_integration(client, test_user_and_token):
#     """
#     Teste de integração com o Ollama real (requer Ollama rodando localmente).
#     ATENÇÃO: Este teste pode ser lento e falhar se o Ollama não estiver acessível.
#     Idealmente, execute-o apenas localmente.
#     """
#     user_model, token = test_user_and_token
#     response = client.get(
#         "/api/v1/recommendations/",
#         headers={"Authorization": f"Bearer {token}"}
#     )
#     assert response.status_code == 200
#     assert len(response.json()) > 0
#     assert "product_id" in response.json()[0]