from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Environments where the public development secret is acceptable. Anything else, including an
# unset ENVIRONMENT, is treated as a deployed environment and must provide its own secret.
LOCAL_ENVIRONMENTS = frozenset({"local", "development", "dev", "test"})

# Public value, shared with the backend's local profile and the root .env.example.
DEV_SERVICE_AUTH_SECRET = "gm-ai-local-dev-secret"

# Values that have been published in this repository and must never protect a deployed service.
PUBLIC_SERVICE_AUTH_SECRETS = frozenset({DEV_SERVICE_AUTH_SECRET, "gm-ai-internal-hmac-secret"})

MIN_SERVICE_AUTH_SECRET_LENGTH = 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Fails closed: without an explicit local/dev/test value the service assumes it is deployed.
    ENVIRONMENT: str = "production"

    AI_SERVICE_NAME: str = "gomech-ai"
    AI_SERVICE_VERSION: str = "1.0.0"
    SERVICE_AUTH_SECRET: str = DEV_SERVICE_AUTH_SECRET

    DEFAULT_PROVIDER: str = "mock"  # mock, openai, gemini
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    GEMINI_API_KEY: str | None = None

    TIMEOUT_SECONDS: float = 15.0
    MAX_RETRIES: int = 3

    LOG_LEVEL: str = "INFO"

    @property
    def is_local(self) -> bool:
        return self.ENVIRONMENT.strip().lower() in LOCAL_ENVIRONMENTS

    @model_validator(mode="after")
    def reject_unsafe_secret_outside_local(self) -> "Settings":
        if self.is_local:
            return self

        secret = self.SERVICE_AUTH_SECRET.strip()
        if secret in PUBLIC_SERVICE_AUTH_SECRETS:
            raise ValueError(
                f"SERVICE_AUTH_SECRET uses a public development value, accepted only when ENVIRONMENT is one "
                f"of {sorted(LOCAL_ENVIRONMENTS)}. Set a unique secret (for example, openssl rand -hex 32)."
            )
        if len(secret) < MIN_SERVICE_AUTH_SECRET_LENGTH:
            raise ValueError(
                f"SERVICE_AUTH_SECRET must be at least {MIN_SERVICE_AUTH_SECRET_LENGTH} characters outside "
                "local environments."
            )
        return self


settings = Settings()
