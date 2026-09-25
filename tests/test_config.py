import pytest
from pydantic import ValidationError

from app.core.config import DEV_SERVICE_AUTH_SECRET, Settings

STRONG_SECRET = "3f9a1c7e5b2d4f6a8c0e1b3d5f7a9c2e"


def build(**overrides) -> Settings:
    return Settings(_env_file=None, **overrides)


@pytest.mark.parametrize("environment", ["local", "development", "dev", "test", "LOCAL"])
def test_dev_secret_is_accepted_in_local_environments(environment):
    settings = build(ENVIRONMENT=environment)

    assert settings.SERVICE_AUTH_SECRET == DEV_SERVICE_AUTH_SECRET


def test_production_is_the_default_environment():
    assert Settings.model_fields["ENVIRONMENT"].default == "production"


@pytest.mark.parametrize("secret", [DEV_SERVICE_AUTH_SECRET, "gm-ai-internal-hmac-secret"])
def test_public_secrets_are_rejected_outside_local(secret):
    with pytest.raises(ValidationError, match="public development value"):
        build(ENVIRONMENT="production", SERVICE_AUTH_SECRET=secret)


def test_short_secret_is_rejected_outside_local():
    with pytest.raises(ValidationError, match="at least 32 characters"):
        build(ENVIRONMENT="staging", SERVICE_AUTH_SECRET="too-short")


def test_strong_secret_is_accepted_in_production():
    settings = build(ENVIRONMENT="production", SERVICE_AUTH_SECRET=STRONG_SECRET)

    assert settings.is_local is False
