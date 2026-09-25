class AiServiceError(Exception):
    def __init__(self, message: str, error_code: str = "AI_SERVICE_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code


class RateLimitError(AiServiceError):
    def __init__(self, message: str = "Provider rate limit exceeded", retry_after: int = 5):
        super().__init__(message, error_code="AI_RATE_LIMIT", status_code=429)
        self.retry_after = retry_after


class TimeoutError(AiServiceError):
    def __init__(self, message: str = "Provider call timed out"):
        super().__init__(message, error_code="AI_TIMEOUT", status_code=504)


class ProviderError(AiServiceError):
    def __init__(self, message: str = "External AI provider error", status_code: int = 502):
        super().__init__(message, error_code="AI_PROVIDER_ERROR", status_code=status_code)


class GuardrailViolationError(AiServiceError):
    def __init__(self, message: str, rule: str = "SAFETY_GUARDRAIL"):
        super().__init__(message, error_code="AI_GUARDRAIL_VIOLATION", status_code=422)
        self.rule = rule
