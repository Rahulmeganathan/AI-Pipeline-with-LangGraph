from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # This will ignore extra fields in .env
    )
    
    # Google Gemini Configuration
    google_api_key: Optional[str] = Field(default=None, validation_alias="GOOGLE_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", validation_alias="GEMINI_MODEL")
    
    # LangSmith Configuration
    langchain_api_key: Optional[str] = Field(default=None, validation_alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="ai_pipeline_demo", validation_alias="LANGCHAIN_PROJECT")
    langchain_tracing_v2: bool = Field(default=True, validation_alias="LANGCHAIN_TRACING_V2")
    
    # OpenWeatherMap Configuration
    openweather_api_key: Optional[str] = Field(default=None, validation_alias="OPENWEATHER_API_KEY")
    
    # Qdrant Configuration
    qdrant_url: Optional[str] = Field(default=None, validation_alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, validation_alias="QDRANT_API_KEY")
    qdrant_collection_name: str = Field(default="documents", validation_alias="QDRANT_COLLECTION_NAME")
    
    # Application Configuration
    chunk_size: int = Field(default=1000, validation_alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, validation_alias="CHUNK_OVERLAP")
    max_tokens: int = Field(default=1000, validation_alias="MAX_TOKENS")
    temperature: float = Field(default=0.7, validation_alias="TEMPERATURE")
    
    # OpenAI Configuration
    openai_model: str = Field(default="gpt-3.5-turbo")


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def init_settings() -> Settings:
    """Initialize settings and return the instance."""
    return get_settings()