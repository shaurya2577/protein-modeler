from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./protein_disease.db"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Data Collection
    max_diseases: int = 200
    min_association_strength: float = 0.3
    
    # Rate Limiting
    requests_per_minute: int = 50
    
    # LLM Provider (anthropic or openai)
    llm_provider: str = "anthropic"
    llm_model: str = "claude-3-5-sonnet-20241022"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

