import re

from app.domain.exceptions import GuardrailViolationError

UNSAFE_AUTOMOTIVE_PATTERNS = [
    (
        re.compile(r"(desativar|remover|desligar|burlar)\s+(o\s+)?(airbag|abs|sensor\s+de\s+oxig[eê]nio)", re.IGNORECASE),
        "UNSAFE_SAFETY_SYSTEM_BYPASS",
        "Proibido sugerir remoção ou bypass de sistemas de segurança obrigatórios (Airbag, ABS).",
    ),
    (
        re.compile(r"(andar|dirigir|rodar)\s+(sem\s+freio|com\s+freio\s+vazando|com\s+pedal\s+no\s+fundo)", re.IGNORECASE),
        "UNSAFE_BRAKE_OPERATION",
        "Risco Crítico: Jamais orientar condução de veículo com falha severa de frenagem.",
    ),
    (
        re.compile(r"(soldar|reparar\s+com\s+solda)\s+(roda\s+de\s+liga|disco\s+de\s+freio)", re.IGNORECASE),
        "UNSAFE_STRUCTURAL_REPAIR",
        "Reparo estrutural proibido por normas técnicas ABNT/SAE em componentes de fadiga crítica.",
    ),
    (
        re.compile(r"(burlar|eliminar|remover)\s+(o\s+)?(catalisador|filtro\s+dpf|arrefecimento)", re.IGNORECASE),
        "UNSAFE_EMISSIONS_BYPASS",
        "Violação regulatória ambiental e de segurança veicular.",
    ),
]

CPF_REGEX = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
CNPJ_REGEX = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_REGEX = re.compile(r"\b(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\d{4}|\d{4})[-.\s]?\d{4}\b")
AUTH_SECRET_REGEX = re.compile(r"\b(?:Bearer\s+[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*|ak-[a-zA-Z0-9]{16,}|sk-[a-zA-Z0-9]{16,})\b")


def check_safety_guardrails(text: str) -> None:
    """Validates that input/output text does not contain hazardous automotive guidance."""
    if not text:
        return

    for pattern, rule_code, message in UNSAFE_AUTOMOTIVE_PATTERNS:
        if pattern.search(text):
            raise GuardrailViolationError(message=message, rule=rule_code)


def sanitize_sensitive_data(text: str) -> str:
    """Sanitizes PII and credentials from prompts and responses."""
    if not text:
        return text

    sanitized = AUTH_SECRET_REGEX.sub("[SECRET_REDACTED]", text)
    sanitized = CNPJ_REGEX.sub("[CNPJ_REDACTED]", sanitized)
    sanitized = CPF_REGEX.sub("[CPF_REDACTED]", sanitized)
    sanitized = EMAIL_REGEX.sub("[EMAIL_REDACTED]", sanitized)
    sanitized = PHONE_REGEX.sub("[PHONE_REDACTED]", sanitized)
    return sanitized
