---
name: dev-postgres-docker
description: >-
  Start, health-check, and connect to the QuieroUnSMS development PostgreSQL
  database defined in docker-compose.yml (official postgres:18.7 image). Use
  whenever the user or task needs local Postgres—migrations (Alembic), SQL
  queries, schema inspection, seeding data, debugging DATABASE_URL, integration
  tests, or mentions docker compose db, quierounsms-postgres, port 5432, psql,
  or postgresql+psycopg—even if they do not say "connect to the database."
---

# Dev PostgreSQL via Docker Compose

This repository runs PostgreSQL **18.7** in Docker. Connection details live in `docker-compose.yml` at the repo root and in `.env.example` as `DATABASE_URL`.

## Canonical configuration

Read `docker-compose.yml` when in doubt; these are the dev defaults:

| Setting | Value |
|---------|-------|
| Compose service | `db` |
| Container name | `quierounsms-postgres` |
| Image | `postgres:18.7` |
| Host port | `5432` → container `5432` |
| User / password | `postgres` / `postgres` |
| Dev database | `quierounsms_dev` |
| Test database | `quierounsms_test` (created on first init via `docker/postgres/init-databases.sql`) |

**App / Alembic URL** (SQLAlchemy + psycopg):

```text
postgresql+psycopg://postgres:postgres@localhost:5432/quierounsms_dev
```

**Integration tests** (`TEST_DATABASE_URL`):

```text
postgresql+psycopg://postgres:postgres@localhost:5432/quierounsms_test
```

From the **host**, plain libpq / `psql` URLs omit `+psycopg`:

```text
postgresql://postgres:postgres@localhost:5432/quierounsms_dev
```

## Workflow

### 1. Ensure the database is running

From the repository root (where `docker-compose.yml` lives):

```bash
docker compose up -d db
```

Wait until healthy (compose defines `pg_isready` healthcheck):

```bash
docker compose ps db
# STATUS should include (healthy)
```

If the container is missing or unhealthy, inspect logs:

```bash
docker compose logs --tail=50 db
```

### 2. Connect with the Docker CLI (preferred for agents)

Use `docker exec` so you do not depend on `psql` installed on the host:

```bash
docker exec -it quierounsms-postgres psql -U postgres -d quierounsms_dev
```

One-off SQL (non-interactive):

```bash
docker exec quierounsms-postgres psql -U postgres -d quierounsms_dev -c "SELECT current_database(), version();"
```

List tables in `public`:

```bash
docker exec quierounsms-postgres psql -U postgres -d quierounsms_dev -c "\dt public.*"
```

Switch database (e.g. test DB):

```bash
docker exec quierounsms-postgres psql -U postgres -d quierounsms_test -c '\conninfo'
```

**Why the container name:** `container_name: quierounsms-postgres` in compose is stable; `docker compose exec db psql ...` also works and tracks the service name instead.

```bash
docker compose exec -T db psql -U postgres -d quierounsms_dev -c 'SELECT 1'
```

Use `-T` when running from scripts or CI-like shells (no TTY).

### 3. Connect from the host (optional)

If `psql` is on the PATH:

```bash
PGPASSWORD=postgres psql -h localhost -p 5432 -U postgres -d quierounsms_dev
```

### 4. Tie-in with the application

- Copy `.env.example` → `.env` and set `DATABASE_URL` to the dev URL above.
- Migrations: `uv run alembic upgrade head` (expects DB up and `DATABASE_URL` set).
- Integration tests: export `TEST_DATABASE_URL` to the test DB URL before `pytest tests/integration`.

## Troubleshooting

| Symptom | What to try |
|---------|-------------|
| Connection refused on `localhost:5432` | `docker compose up -d db`; confirm `docker compose ps` shows port mapping |
| `database "quierounsms_dev" does not exist` | Fresh volume issue—check init ran; list DBs: `docker exec quierounsms-postgres psql -U postgres -c '\l'` |
| `quierounsms_test` missing | Init script only runs on **empty** data volume; recreate volume if needed (`docker compose down -v` then `up -d db`—**destroys local DB data**) |
| Auth failed | Credentials are dev-only from compose; do not guess—re-read `POSTGRES_USER` / `POSTGRES_PASSWORD` |
| Port 5432 in use | Another Postgres on host; change compose port mapping or stop the other service |

## Safety

- Default credentials are for **local development only**; never use them in production.
- Prefer read-only inspection (`SELECT`, `\d`, `\dt`) unless the user explicitly asks to mutate data.
- Before `docker compose down -v`, warn that all data in the Postgres volume will be lost.

## Quick reference

```bash
# Start + health
docker compose up -d db && docker compose ps db

# Shell into psql (dev)
docker exec -it quierounsms-postgres psql -U postgres -d quierounsms_dev

# Prove connectivity
docker exec quierounsms-postgres pg_isready -U postgres
```