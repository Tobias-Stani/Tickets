# Tickets

Support ticket system: admins manage users, tags and topics and answer tickets;
clients open tickets (up to 3 images) and follow the conversation.

Design: [docs/DESIGN.md](docs/DESIGN.md)

## Stack

FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL · Jinja2 + HTMX + Tailwind CSS · Python 3.14

## Run locally with Docker

1. Create `.env` in the project root:

   ```env
   SECRET_KEY=change-me-to-a-long-random-string
   DATABASE_URL=postgresql://tickets:tickets@db:5432/tickets
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=change-me-please
   ```

2. Start everything:

   ```sh
   docker-compose up --build
   ```

   App: http://localhost:8010 (sign in with `ADMIN_EMAIL` / `ADMIN_PASSWORD`)

On startup the container runs migrations, seeds the admin (idempotent) and starts
the server. The `tailwind` service rebuilds CSS when templates change.

### Live reload

`app/` is mounted into the container and uvicorn runs with `--reload`: code and
template changes apply on save. Restart only when:

| Change                          | Command                      |
| ------------------------------- | ---------------------------- |
| New migration                   | `docker-compose restart web` |
| New dependency (pyproject.toml) | `docker-compose up -d --build` |

Host ports default to `8010` (app) and `5434` (Postgres); override them with
`WEB_HOST_PORT` / `DB_HOST_PORT` in `.env`.

## Environment variables

| Variable                 | Required | Default         | Notes                                   |
| ------------------------ | -------- | --------------- | --------------------------------------- |
| `SECRET_KEY`             | yes      |                 | Signs session cookies                   |
| `DATABASE_URL`           | yes      |                 | `postgresql://` is accepted             |
| `ADMIN_EMAIL`            | yes      |                 | Initial admin, created once             |
| `ADMIN_PASSWORD`         | yes      |                 |                                         |
| `ADMIN_FULL_NAME`        | no       | `Administrator` |                                         |
| `HTTPS_ONLY_COOKIES`     | no       | `true`          | Set `false` only for local HTTP         |
| `PORT`                   | no       | `8000`          | Railway sets it automatically           |

## Development without Docker

```sh
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest          # tests use in-memory SQLite, no services needed
.venv/bin/ruff check .
```

New migration after changing models:

```sh
.venv/bin/alembic revision --autogenerate -m "describe change"
```

## Project layout

```
app/
├── core/        # config, db, security, storage, csrf, errors
├── shared/      # base model, generic repository, pagination
├── modules/     # one folder per feature: models → repository → service → router
└── templates/   # layouts, reusable components (macros), pages
```
