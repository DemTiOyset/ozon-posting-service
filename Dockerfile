FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# системные зависимости (для сборки некоторых пакетов)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ставим uv (быстрый менеджер зависимостей)
RUN pip install --no-cache-dir uv

# сначала копируем только файлы зависимостей (кэш Docker будет работать корректно)
COPY pyproject.toml uv.lock ./

# устанавливаем зависимости строго по lock
RUN uv sync --frozen --no-dev

# копируем проект
COPY . .

EXPOSE 8000

# запускаем через uv (использует .venv внутри контейнера)
CMD ["uv", "run", "uvicorn", "application.main:app", "--host", "0.0.0.0", "--port", "8000"]

