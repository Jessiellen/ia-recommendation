import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.api'] = MagicMock()
sys.modules['chromadb.api.types'] = MagicMock()

try:
    import pysqlite3
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Any

from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
from app.core.config import settings
from app.auth.jwks import create_access_token, get_password_hash
from app.models.user import User
from app.agents.recommendation_agent import RecommendationAgent


def pytest_configure(config):
    """
    Hook do pytest para configurar antes de qualquer teste ser executado.
    Garanti que as variáveis de ambiente necessárias para a classe Settings sejam carregadas.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dotenv_path = os.path.join(project_root, ".env.test")

    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        print(f"\n--- DEBUG: .env.test carregado de: {dotenv_path} ---")
        print(f"--- DEBUG: DATABASE_URL definido: {os.getenv('DATABASE_URL') is not None} ---")
        print(f"--- DEBUG: SECRET_KEY definido: {os.getenv('SECRET_KEY') is not None} ---")
        print(f"--- DEBUG: TESTING definido: {os.getenv('TESTING') == 'True'} ---")
    else:
        print(f"\n--- ERRO CRÍTICO: .env.test NÃO ENCONTRADO em: {dotenv_path} ---")

    settings.DATABASE_URL = "sqlite:///:memory:"

TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(setup_test_database):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session: Session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_token(db_session: Session):
    admin_user = User(username="admin", email="admin@example.com", hashed_password=get_password_hash("adminpassword"))
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)
    return create_access_token({"sub": admin_user.username})

@pytest.fixture
def user_token(db_session: Session):
    regular_user = User(username="alice", email="alice@example.com", hashed_password=get_password_hash("alicepassword"))
    db_session.add(regular_user)
    db_session.commit()
    db_session.refresh(regular_user)
    return create_access_token({"sub": regular_user.username})

@pytest.fixture
def mock_recommendation_agent(mocker):
    mock_chat_ollama_class = mocker.patch('app.agents.recommendation_agent.ChatOllama')
    mock_ollama_instance = mock_chat_ollama_class.return_value

    default_response_content = """
Product ID: 101, Name: Smartwatch X2, Reason: Ótimo para monitoramento de saúde e notificações.
Product ID: 102, Name: Fone Bluetooth Pro, Reason: Qualidade de áudio superior e confortável.
Product ID: 103, Name: E-reader Lumina, Reason: Ideal para leitura digital com tela confortável.
"""
    mock_ollama_instance.invoke.return_value = MagicMock(content=default_response_content)

    mock_agent_instance = mocker.Mock(spec=RecommendationAgent)
    mock_agent_instance.generate_recommendations.return_value = [
        {"product_id": 991, "product_name": "Mocked Book", "reason": "Mocked reason for book."},
        {"product_id": 992, "product_name": "Mocked Headphones", "reason": "Mocked reason for headphones."},
    ]
    mocker.patch('app.api.endpoints.recommendations.recommendation_agent_instance', new=mock_agent_instance)

    yield mock_agent_instance