from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
import os
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = Field(
        default="sqlite:///:memory:",
        description="Database connection URL"
    )
    
    SECRET_KEY: SecretStr = Field(
        default=SecretStr("dummy-secret-for-tests"),
        description="Secret key for JWT tokens"
    )
    
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Token expiration time in minutes"
    )
    
    OLLAMA_BASE_URL: str = Field(
        default="http://mock-ollama:11434",
        description="Ollama server base URL"
    )
    
    DB_ECHO_LOGS: bool = Field(
        default=False,
        description="Enable SQLAlchemy logs"
    )
    
    TESTING: bool = Field(
        default=True,
        description="Flag to indicate testing environment"
    )

    model_config = SettingsConfigDict(
        env_file=".env.test" if os.path.exists(".env.test") else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()