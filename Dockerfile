FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd --system gomech \
    && useradd --system --gid gomech --no-create-home --shell /usr/sbin/nologin gomech

COPY app ./app

# Run as an unprivileged user; port 8000 does not need root.
USER gomech

EXPOSE 8000

# Cloud Run injects PORT; fall back to 8000 for local runs. Hot reload is enabled by docker-compose, never here.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
