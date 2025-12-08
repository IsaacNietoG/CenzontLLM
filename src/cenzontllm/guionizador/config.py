from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    RUN_MODE: Literal["mock", "groq", "ollama"] = "mock"
    GROQ_API_KEY: str = ""
    MODEL: str = "llama-3.3-70b-versatile"  # Groq, o "llama3.1:70b" para Ollama

    NUM_GUESTS: int = 1
    MAX_REPLICA_ROUNDS: int = 2
    TARGET_MINUTES: int = 20

    class Config:
        env_prefix = "CENZONT_"
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
