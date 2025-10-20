FROM python:3.13.7-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=2.1.4

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
    && pip install --no-cache-dir poetry==${POETRY_VERSION} \
    && apt-get purge -y build-essential curl \
    && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --without dev

COPY ./core ./core
COPY ./apps/worker ./apps/worker

CMD ["celery", "-A", "apps.worker", "worker", "--loglevel=INFO", "--concurrency=2"]