from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5235/platform",
        description="PostgreSQL database URL",
    )

    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API key for Claude",
    )

    server_host: str = Field(default="0.0.0.0", description="Server host")
    server_port: int = Field(default=5005, description="Server port")

    log_level: str = Field(default="INFO", description="Logging level")


settings = Settings()
