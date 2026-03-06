"""
rules-engine/src/config.py — Environment configuration for the Rules Engine.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    rabbitmq_url:      str = "amqp://guest:guest@rabbitmq:5672/"
    rabbitmq_exchange: str = "mars.events"

    redis_url:         str = "redis://redis:6379"

    postgres_dsn:      str = "postgresql+asyncpg://mars:mars@postgres:5432/mars"

    simulator_base_url: str = "http://simulator:8080"

    # Redis TTL for latest-state keys (seconds)
    state_ttl: int = 3600


settings = Settings()
