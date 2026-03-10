"""Configuration loaded from .env via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    bybit_testnet: bool = True
    bybit_api_key: str = ""
    bybit_api_secret: str = ""

    # Position mode for linear: "one_way" (positionIdx=0) or "hedge" (1=Buy, 2=Sell). If unset, inferred from positions.
    bybit_position_mode: str = ""

    redis_enabled: bool = False
    redis_url: str = "redis://redis:6379/0"


settings = Settings()
