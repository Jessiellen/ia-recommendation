from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

TESTING = os.getenv("TESTING", "False").lower() in ("true", "1", "t")

if TESTING:
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL + "_test"
else:
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Verifica  antes de usar
    echo=settings.DEBUG  # Mostra SQL no log em modo debug
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  
)

Base = declarative_base()

def get_db():
  
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

def drop_tables():
    Base.metadata.drop_all(bind=engine)

def get_test_db():

    db = SessionLocal()
    transaction = db.begin()
    try:
        yield db
    finally:
        transaction.rollback()
        db.close()