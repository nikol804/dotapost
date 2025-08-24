FROM python:3.11-slim

# System deps
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app

# Install dependencies first (better cache)
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN useradd -m appuser \
    && chown -R appuser:appuser /app
USER appuser

# Collect static (idempotent)
RUN python manage.py collectstatic --noinput || true

# Default healthcheck command
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import socket; s=socket.socket(); s.settimeout(3); s.connect(('127.0.0.1', 8000)); s.close()" || exit 1

# Default port
EXPOSE 8000

# Entrypoint allows overriding command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


