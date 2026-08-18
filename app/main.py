from os import getenv

from fastapi import FastAPI


app = FastAPI(title="GoMech AI Service", version="0.1.0")


@app.get("/")
def root() -> dict[str, str]:
    return {"service": getenv("AI_SERVICE_NAME", "gomech-ai"), "status": "ok"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
