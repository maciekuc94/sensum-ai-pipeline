# Roadmap

SENSUM currently runs as a **filesystem-based pipeline**: stage state is detected by
scanning for marker files on disk, and a read-only FastAPI dashboard
(Mission Control) renders that state. This roadmap tracks the path from there to a
**complete, database-backed, deployed** version.

Phases are ordered by dependency — each one builds on the previous — and each is
**independently shippable**: every phase ends in a coherent improvement you can stop
at, with its own feature branch and pull request.

## At a glance

| Phase | Focus | Stack | Status |
| --- | --- | --- | --- |
| 1 | Persistence | PostgreSQL · SQLAlchemy 2.0 · Alembic | Planned |
| 2 | Containerization | Docker · docker-compose | Planned |
| 3 | Continuous Integration | GitHub Actions · pytest · ruff | Planned |
| 4 | Deployment | Railway / Render · managed Postgres | Planned |
| 5 | Interactive control *(stretch)* | FastAPI · background jobs | Planned |

---

## Phase 1 — Persistence (PostgreSQL)

**Goal.** Replace filesystem-marker state detection with a relational database as the
source of truth for pipeline state — unlocking history, timestamps, and richer queries
the filesystem can't express.

**Scope.**
- Schema: `video` (slug), `stage` (per-slug stage status), `artifact`, `backlog_item`.
- SQLAlchemy 2.0 models + Alembic migrations (reproducible from scratch).
- A **scanner / ingest job** that reads the existing filesystem markers and populates
  the database — a bridge that preserves the current detection logic instead of
  throwing it away.
- Mission Control reads state from the database instead of scanning the filesystem.

**Stack.** PostgreSQL · SQLAlchemy 2.0 · Alembic

**Done when.** The dashboard renders entirely from the database; the scanner keeps the
database in sync with on-disk artifacts; migrations rebuild the schema from zero.

> The database becomes the new source of truth for *state*; the filesystem remains the
> *artifact store* (scripts, images, audio).

## Phase 2 — Containerization (Docker)

**Goal.** A reproducible, OS-independent environment.

**Scope.**
- `Dockerfile` (slim Python base) + `docker-compose.yml` (app + Postgres, optionally
  Adminer for a DB GUI).
- Configuration via `.env`.
- Removes Windows-specific encoding workarounds (`PYTHONIOENCODING`) — everything runs
  in Linux containers.

**Stack.** Docker · docker-compose

**Done when.** `docker compose up` brings up the app and database together and serves
the dashboard, with no host Python install required.

## Phase 3 — Continuous Integration (GitHub Actions)

**Goal.** An automated quality gate on every push.

**Scope.**
- `.github/workflows/ci.yml`: lint (ruff) + tests (pytest), with Postgres as a service
  container for tests that need a database.
- Status badge in the README.

**Stack.** GitHub Actions · pytest · ruff

**Done when.** CI runs on every push and pull request, blocks merge on failure, and the
badge reads green.

## Phase 4 — Deployment

**Goal.** A publicly reachable dashboard.

**Scope.**
- Deploy to Railway or Render with a managed Postgres instance.
- Run migrations automatically on deploy.
- Live URL added to the README.

**Stack.** Railway / Render · managed PostgreSQL

**Done when.** A public URL serves the dashboard against a hosted database.

## Phase 5 — Interactive control *(stretch)*

**Goal.** Turn the read-only viewer into a control surface.

**Scope.**
- Write operations: update stage status, attach notes.
- Eventually, trigger pipeline stages from the UI via background tasks / a job queue
  (FastAPI BackgroundTasks → a queue such as RQ/arq if needed).

**Stack.** FastAPI · background jobs

**Done when.** A stage can be marked and advanced from the UI — and ultimately
triggered — rather than only viewed.

---

## Working principles

- **One feature branch per phase** (`feat/postgres-persistence`, `feat/docker`, …) →
  pull request into `main`.
- **Independently shippable** — each phase stands on its own; stop after any of them and
  the project is still coherent.
- **Database = source of truth for state; filesystem = artifact store.**
- **Tests accompany each phase**, not bolted on afterward.
- **Design before code** — start each phase by agreeing the schema / interface, then
  implement.
