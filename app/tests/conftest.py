import pytest
from app.database import Base, get_test_db, create_tables, drop_tables, get_db 
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import text

@pytest.fixture(scope="session")
def setup_test_database():
    """Configuração do banco de dados de teste"""
    create_tables()
    yield
    drop_tables()

@pytest.fixture
def db_session(setup_test_database):
    """Fornece uma sessão de banco de dados para testes"""
    for db in get_test_db():
        yield db

@pytest.fixture
def client():
    """Cliente de teste FastAPI"""
    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()