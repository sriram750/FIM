from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import os


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    APP_NAME: str = "FIM Enterprise"
    APP_VERSION: str = "1.0.0"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    API_V1_STR: str = "/api/v1"

    # Cryptography & Security
    SECRET_KEY: str = "change_this_to_a_super_secret_cryptographic_key_with_at_least_64_bytes"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENROLLMENT_TOKEN_SECRET: str = "change_this_enrollment_token_secret"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str):
            return json.loads(v)
        return v

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "fim_admin"
    POSTGRES_PASSWORD: str = "change_this_postgres_secure_password"
    POSTGRES_DB: str = "fim_enterprise"
    DATABASE_URL: str = "sqlite+aiosqlite:///./fim_local.db"
    DATABASE_SYNC_URL: str = "sqlite:///./fim_local.db"

    # Redis Queue & Streams
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "change_this_redis_secure_password"
    REDIS_STREAM_KEY: str = "fim:events:incoming"
    REDIS_GROUP_NAME: str = "fim-workers"
    REDIS_CONSUMER_NAME: str = "worker-1"

    # OpenSearch
    OPENSEARCH_HOST: str = "localhost"
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_USER: str = "admin"
    OPENSEARCH_PASSWORD: str = "change_this_opensearch_secure_password"
    OPENSEARCH_USE_SSL: bool = False
    OPENSEARCH_INDEX_PREFIX: str = "fim-events"

    # Default Bootstrap Admin
    INITIAL_ADMIN_EMAIL: str = "admin@fim.local"
    INITIAL_ADMIN_PASSWORD: str = "Admin@FIM2026!Secure"
    INITIAL_ADMIN_NAME: str = "Security Administrator"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
