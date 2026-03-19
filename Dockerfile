FROM python:3.13.5-alpine

ADD https://astral.sh/uv/install.sh /uv-installer.sh

RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.10.9 /uv /uvx /bin/

RUN mkdir -p /app

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src ./src
COPY templates ./templates
COPY tests ./tests
COPY alembic ./alembic
COPY alembic.ini main.py ./

ENV UV_NO_DEV=0
ENV PYTHONPATH=/app

# Sync dependencies (better caching)
RUN uv sync --extra dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
