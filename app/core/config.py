from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    AI_SERVICE_NAME: str = "gomech-ai"
    AI_SERVICE_VERSION: str = "1.0.0"
    SERVICE_AUTH_SECRET: str = "gm-ai-internal-hmac-secret"

    DEFAULT_PROVIDER: str = "mock"  # mock, openai, gemini
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    GEMINI_API_KEY: str | None = None

    TIMEOUT_SECONDS: float = 15.0
    MAX_RETRIES: int = 3

    LOG_LEVEL: str = "INFO"


settings = Settings()
