# Use a builder stage to install dependencies with uv
FROM python:3.13-alpine AS builder

# install uv for the build only
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app
# copy project metadata for dependency installation
COPY pyproject.toml uv.lock ./

# install dependencies into the system location based on the project
RUN uv pip install --system --no-cache -r pyproject.toml

# final runtime image
FROM python:3.13-alpine
LABEL org.opencontainers.image.source="https://github.com/jhjcpishva/webhook-to-nats"
WORKDIR /app

# copy installed dependencies, excluding the uv binary
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# copy application code
COPY . /app

CMD ["python", "main.py"]
