FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry and add to PATH
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy Poetry configuration
COPY pyproject.toml poetry.lock* ./

# Install dependencies only (not the current project)
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root

# Copy application code
COPY ruler_server ./ruler_server
COPY output_schema ./output_schema
COPY static ./static
COPY expense_rulebook.json ./expense_rulebook.json
COPY expense_rulebook.schema.json ./expense_rulebook.schema.json
COPY config.toml ./config.toml

EXPOSE 8810

CMD ["poetry", "run", "ruler-server"]


