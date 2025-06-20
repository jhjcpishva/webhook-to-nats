# === Build stage ===
FROM python:3.13-alpine AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv pip install --system --no-cache -r pyproject.toml

# === Final stage ===
FROM python:3.13-alpine
LABEL org.opencontainers.image.source="https://github.com/jhjcpishva/webhook-to-nats"

WORKDIR /app
COPY --from=builder /usr/local /usr/local

COPY . /app

CMD ["python", "main.py"]
