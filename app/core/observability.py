import json
import logging
import sys
from typing import Any

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

# Prometheus Metrics Definitions
AI_REQUESTS_TOTAL = Counter(
    "ai_requests_total",
    "Total AI requests received by capability and status",
    ["capability", "provider", "status"],
)

AI_REQUEST_LATENCY = Histogram(
    "ai_request_latency_seconds",
    "AI request latency distribution in seconds",
    ["capability", "provider"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 15.0),
)

AI_TOKENS_TOTAL = Counter(
    "ai_tokens_total",
    "Total tokens consumed across capabilities",
    ["capability", "type"],
)

AI_GUARDRAIL_VIOLATIONS = Counter(
    "ai_guardrail_violations_total",
    "Total guardrail safety violations blocked",
    ["capability", "rule"],
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "tenant_id"):
            log_data["tenant_id"] = record.tenant_id
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id
        if hasattr(record, "capability"):
            log_data["capability"] = record.capability
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(log_level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]


logger = logging.getLogger("gomech.ai")


def get_metrics_data() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
