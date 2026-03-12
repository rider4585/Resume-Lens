"""Application settings loaded from environment."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings from env vars. Use .env file in development."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Ollama (local LLM) - no API key required
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_embedding_model: str = "nomic-embed-text"
    use_rag: bool = True

    database_url: str = "sqlite:///./matches.db"
    storage_root: str = "storage"


def get_settings() -> Settings:
    """Return application settings (singleton-style)."""
    return Settings()
