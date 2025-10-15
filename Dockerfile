FROM python:3.13.7-slim

ARG BUILD_ENV=development

ENV APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    # Python's configuration:
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Poetry's configuration:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    PATH="${POETRY_HOME}/bin:/root/.local/bin:${PATH}" \
    POETRY_VERSION=2.1.4


RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN poetry install $(test "$BUILD_ENV" = "production" && echo "--only=main") --no-interaction --no-ansi

COPY . /code

EXPOSE 8000

CMD ["uvicorn", "src.web.app:app", "--host", "${APP_HOST}", "--port", "${APP_PORT}"]
