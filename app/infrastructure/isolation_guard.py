import sys

PROHIBITED_DB_MODULES = {
    "psycopg",
    "psycopg2",
    "asyncpg",
    "sqlalchemy",
    "pg8000",
    "mysql",
    "aiomysql",
    "tortoise",
    "databases",
    "peewee",
    "django.db",
}


def verify_zero_database_isolation() -> bool:
    """
    Runtime isolation guard:
    Verifies that the standalone AI service has zero database drivers or ORM modules loaded.
    This guarantees that the AI service remains strictly stateless and cannot bypass domain repositories.
    """
    loaded_prohibited = [mod for mod in PROHIBITED_DB_MODULES if mod in sys.modules]
    if loaded_prohibited:
        raise RuntimeError(
            f"ARCHITECTURAL VIOLATION (ADR-019): The AI service must not connect to or import database drivers. "
            f"Prohibited modules detected: {', '.join(loaded_prohibited)}"
        )
    return True
