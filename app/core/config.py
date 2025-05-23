from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DB_ECHO_LOGS: bool = False 

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()