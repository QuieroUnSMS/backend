# QuieroUnSMS Backend

Official **QuieroUnSMS** API

## Requirements

- Python **3.15.2** (see `.python-version`; use `uv python install 3.15.2`)
- PostgreSQL **18.7** (Docker Compose below)

## Database (Docker)

```bash
docker compose up -d db
```

Wait until healthy, then set URLs:

| Use | URL |
|-----|-----|
| App / Alembic | `postgresql+psycopg://postgres:postgres@localhost:5432/quierounsms_dev` |
| Integration tests | `postgresql+psycopg://postgres:postgres@localhost:5432/quierounsms_test` |

Copy `.env.example` to `.env` for the app `DATABASE_URL`.

## Install and run

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --app-dir src
```

API docs: http://localhost:8000/docs

## Tests

```bash
uv run pytest tests/unit -q
export TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/quierounsms_test
uv run pytest tests/integration -q
```

Full validation: [specs/001-starting-point/quickstart.md](specs/001-starting-point/quickstart.md)