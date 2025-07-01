import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:super#@localhost:5433/decision_db")
    LLM_BACKEND: str = os.getenv("LLM_BACKEND", "ollama")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma3:4b-it-qat")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")

settings = Settings()
