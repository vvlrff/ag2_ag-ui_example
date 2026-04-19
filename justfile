set shell := ["bash", "-uc"]

default:
    @just --list

# Sync dependencies (run after pulling or editing pyproject.toml).
install:
    uv sync

# Start PostgreSQL in the background.
db-up:
    docker compose up -d db

# Apply migrations.
migrate:
    uv run alembic upgrade head

# Run the dev server with auto-reload.
dev:
    uv run uvicorn ag2_example.main.entrypoint:app --reload

# Bring up the full stack (backend + db).
up:
    docker compose up --build

# Run all tests.
test:
    uv run pytest

# Run only unit tests (no DB required).
test-unit:
    uv run pytest tests/unit

# Lint imports against .importlinter contracts.
lint-imports:
    uv run lint-imports

# Ruff check + format.
lint:
    uv run ruff check src tests
    uv run ruff format --check src tests

# Auto-fix lint issues and format.
fmt:
    uv run ruff check --fix src tests
    uv run ruff format src tests

# Run mypy.
typecheck:
    uv run mypy src tests

# Create a new Alembic revision (just revision "name here").
revision message:
    uv run alembic revision --autogenerate -m "{{message}}"
