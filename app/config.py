
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API keys
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    youtube_api_key: Optional[str] = None
    brave_search_api_key: Optional[str] = None

    # Current model IDs (override through .env)
    # gemini-3.6-flash was never a real Gemini model id and would fail on
    # every call. gemini-3.5-flash is Google's current GA flash model
    # (the "gemini-flash-latest" alias points here as of mid-2026).
    gemini_model: str = "gemini-3.5-flash"
    groq_model: str = "llama-3.3-70b-versatile"
    openrouter_default_model: str = "openrouter/free"

    # Routing
    default_llm_provider: str = "gemini"
    research_provider: str = "gemini"
    fact_check_provider: str = "gemini"
    research_depth: str = "deep"

    # Pipeline
    max_research_queries: int = 15
    max_sources: int = 50
    max_fact_check_rounds: int = 3
    max_writer_agents: int = 4
    max_judge_agents: int = 4
    max_rewrite_rounds: int = 3
    target_quality_score: float = 8.5

    log_level: str = "INFO"
    data_dir: str = "data"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

settings = Settings()
