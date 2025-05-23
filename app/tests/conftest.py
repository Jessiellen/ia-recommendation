import sys
import os
from unittest.mock import patch, MagicMock
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Any

sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.api'] = MagicMock()
sys.modules['chromadb.api.types'] = MagicMock()

try:
    import pysqlite3
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

def pytest_configure(config):
    """Configuração inicial do pytest"""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env.test")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"\nVariáveis de teste carregadas de: {env_path}")
    else:
        print("\nUsando configurações padrão para testes")

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def setup_test_database():
    """Configura o banco de dados de teste"""
    from app.database import Base
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(setup_test_database) -> Generator[Session, None, None]:
    """Sessão do banco de dados para testes"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def client(db_session: Session):
    """Cliente de teste FastAPI"""
    from app.main import app
    from app.database import get_db
    from fastapi.testclient import TestClient
    
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.rollback()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user(db_session: Session):
    """Usuário admin para testes"""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_token(admin_user):
    """Token JWT para o admin"""
    from app.core.security import create_access_token
    return create_access_token({"sub": admin_user.username})

@pytest.fixture
def mock_recommendation_agent():
    """Mock do agente de recomendação"""
    with patch('app.agents.recommendation_agent.ChatOllama') as mock_ollama:
        mock_instance = mock_ollama.return_value
        mock_instance.invoke.return_value = MagicMock(content="""
            Product ID: 101, Name: Smartwatch, Reason: Ótimo para saúde
            Product ID: 102, Name: Fone, Reason: Qualidade de áudio
            Product ID: 103, Name: E-reader, Reason: Leitura confortável
        """)
        
        with patch('app.api.endpoints.recommendations.RecommendationAgent') as mock_agent:
            mock_instance = mock_agent.return_value
            mock_instance.generate_recommendations.return_value = [
                {"product_id": 101, "product_name": "Mocked", "reason": "Test"}
            ]
            yield mock_instance