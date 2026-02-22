FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates curl \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

# создаём окружение и синкаем зависимости в него
RUN uv venv /opt/venv
RUN uv sync --frozen --no-dev

# делаем venv “дефолтным” для всех команд (gunicorn, alembic, etc.)
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["python", "-m", "gunicorn", "application.main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "2", "--timeout", "60"]
