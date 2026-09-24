# Ticket System — Design

## 1. Overview

Support ticket system with two roles:

- **Admin**: manages users, tags and topics; sees and answers every ticket.
- **Client**: creates tickets, sees only their own tickets and replies to them.

Responsive web app (desktop and mobile), deployed on Railway with Docker.

## 2. Stack

| Concern        | Choice                                             |
| -------------- | -------------------------------------------------- |
| Web framework  | FastAPI                                            |
| ORM/migrations | SQLAlchemy 2 + Alembic                             |
| Database       | PostgreSQL                                         |
| UI             | Jinja2 templates + HTMX + Tailwind CSS (standalone CLI, no Node) |
| Auth           | Server-side session cookie + CSRF token            |
| Passwords      | Argon2 hashing                                     |
| Image storage  | Postgres (`stored_files` table) behind a `Storage` port |
| Tests          | pytest (TDD)                                       |
| Lint/format    | Ruff                                               |

Single deployable service. Only Python in the stack. Python 3.14 everywhere (local and Docker) to avoid version drift.

## 3. Domain Model

```
User 1 ──── * Ticket 1 ──── * TicketMessage
                 1
                 └──── 0..3 TicketImage
User * ──── * Tag
Topic 1 ──── * Ticket
```

### User
| Field          | Type      | Notes                         |
| -------------- | --------- | ----------------------------- |
| id             | int PK    |                               |
| email          | str       | unique, login identifier      |
| full_name      | str       |                               |
| password_hash  | str       | Argon2                        |
| role           | enum      | `ADMIN` \| `CLIENT`           |
| is_active      | bool      | inactive users cannot log in  |
| ticket_count   | int       | +1 per created ticket, no reset |
| created_at     | datetime  |                               |

### Tag
Labels attached to users (e.g. plan: "Pro", "Basic").
`id`, `name` (unique), `color`. Many-to-many with User via `user_tags`.

### Topic
Ticket categories. `id`, `name` (unique), `is_active`.
Soft delete (`is_active = false`) so historical tickets keep their topic.

### Ticket
| Field        | Type     | Notes                          |
| ------------ | -------- | ------------------------------ |
| id           | int PK   |                                |
| client_id    | FK User  |                                |
| topic_id     | FK Topic | only active topics selectable  |
| subject      | str      |                                |
| description  | text     |                                |
| status       | enum     | see state machine              |
| created_at   | datetime |                                |
| updated_at   | datetime |                                |

### TicketImage
Images attached when the ticket is created (0 to 3 per ticket).
`id`, `ticket_id`, `object_key` (key in `Storage`), `content_type`, `created_at`.

### TicketMessage
Reply history. `id`, `ticket_id`, `author_id`, `body`, `created_at`.

## 4. Ticket State Machine

States: `OPEN`, `IN_PROGRESS`, `ANSWERED`, `CLOSED`.

| Event                                  | Resulting status        |
| -------------------------------------- | ----------------------- |
| Client creates ticket                  | `OPEN`                  |
| Admin replies                          | `ANSWERED`              |
| Client replies to `ANSWERED` ticket    | `OPEN`                  |
| Admin takes the ticket                 | `IN_PROGRESS` (manual)  |
| Admin closes the ticket                | `CLOSED` (manual)       |

Rules (enforced in the service layer, never only in the UI):

- `CLOSED` is terminal: no replies, no status changes. A new ticket must be created.
- Only admins change status manually.
- Clients cannot close tickets.

## 5. Business Rules

- Only admins create users, of either role (`ADMIN` or `CLIENT`). There is no
  public sign-up.
- Admins activate/deactivate users. `is_active` is checked on every request,
  so deactivation takes effect immediately. An admin cannot deactivate themselves.
- The first admin is seeded automatically on startup from env vars
  (`ADMIN_EMAIL`, `ADMIN_PASSWORD`). Idempotent: skipped if the email exists.
- Forgotten passwords: the user contacts an admin, who sets a new one.
- Clients only access their own tickets (ownership checked in the service layer).
- Creating a ticket increments `client.ticket_count` in the same transaction.
- Images: optional, up to 3 per ticket, `jpg/png/webp`, max 5 MB each.
  Type validated by file content, not only extension. Served through an app
  endpoint that checks ticket visibility, never public.
- Image bytes are stored in Postgres (`stored_files`) through the `Storage` port.
  Stored in the same transaction as the ticket, so failures leave no orphans.
  Switching to an object store (Railway Bucket) later means adding a new
  `Storage` adapter only; services and tests stay unchanged.

## 6. Screens

**Client**
- Login
- My tickets (list with status badges)
- New ticket (topic, subject, description, up to 3 images) — simple, mobile-first form
- Ticket detail (conversation + reply box, disabled when `CLOSED`)

**Admin**
- Ticket dashboard: all tickets, filter by status / client / topic, pagination
- Ticket detail: conversation, reply, change status
- Users: CRUD, activate/deactivate, assign tags, see `ticket_count`
- Tags: CRUD
- Topics: CRUD (soft delete)

## 7. Architecture

Feature-based modules (screaming architecture), each split in layers:

```
router  →  service  →  repository  →  SQLAlchemy models
(HTTP)     (rules)     (data access)
```

- **router**: HTTP only — parse input, call service, render template. No logic.
- **service**: business rules and state machine. Framework-agnostic, unit tested.
- **repository**: queries only. No business rules.
- **schemas**: Pydantic input/output validation.

```
app/
├── main.py                 # app factory
├── core/                   # config, db session, security, storage, errors
├── shared/                 # base model, pagination, template helpers
├── modules/
│   ├── auth/
│   ├── users/
│   ├── tags/
│   ├── topics/
│   └── tickets/
│       ├── models.py
│       ├── schemas.py
│       ├── repository.py
│       ├── service.py
│       ├── state_machine.py
│       └── router.py
├── templates/
│   ├── layouts/
│   ├── components/         # reusable partials (badge, table, form field, modal)
│   └── <module>/
└── static/
migrations/
tests/
```

### Code conventions
- Functions short and single-purpose (target < 20 lines).
- Files focused on one responsibility (target < 150 lines).
- Dependencies injected via FastAPI `Depends`; services receive repositories.
- Type hints everywhere; Ruff enforced.
- Reusable UI via Jinja macros/partials, never copy-pasted markup.

## 8. Infrastructure

- **Dockerfile**: multi-stage — stage 1 builds Tailwind CSS with the standalone
  CLI, stage 2 is a slim Python runtime.
- **docker-compose.yml** (local): `web`, `tailwind` (CSS watcher), `db` (Postgres).
- **Startup**: `alembic upgrade head` → seed admin → `uvicorn`.
- **Railway**: `web` service (Dockerfile) + Postgres.
  Config via env vars (`DATABASE_URL`, `SECRET_KEY`, `ADMIN_*`).

## 9. Out of Scope (for now)

- Monthly counter reset / billing cycles
- Attachments on replies
- Self-service password recovery (admin resets passwords)

## 10. Future Stages

### Email notifications
Planned triggers:
- Client: admin replied, ticket closed.
- Admin: new ticket created, client replied.

Design hook: services are the only place where ticket state changes, so
they are the single point to raise domain events (`TicketCreated`,
`TicketReplied`, `TicketStatusChanged`). A future `notifications` module
subscribes to those events and sends emails through a `Mailer` port
(SMTP/Resend/SendGrid adapter), ideally in a background worker so sending
never blocks the request. No changes to routers or repositories required.

### Other candidates
- Monthly counter reset per billing cycle.
- Self-service password reset by email.
- Attachments on replies.
