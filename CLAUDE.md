# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JAM (Job Application Manager) is a full-stack web app for managing job applications, interviews, contacts, and tracking status/progress/deadlines. It features email-based job scraping, AI-powered job rating, Stripe payments, and a Chrome extension for LinkedIn scraping.

## Commands

### Running the App

```bash
# Windows — starts 3 terminals: frontend, backend API (port 8000), backend scheduler (port 8001)
./run.bat

# Backend only (API)
cd backend && uvicorn app.main:app --reload --port 8000

# Backend scheduler (runs background jobs)
cd backend && SCHEDULER=true uvicorn app.main:app --reload --port 8001

# Frontend
cd frontend && npm start
```

### Backend

```bash
# Install (from repo root)
pip install -e ".[dev]"

# Run all backend tests (parallel)
pytest -n auto ./backend

# Run a single test file
pytest backend/tests/core/test_auth.py

# Run a single test
pytest backend/tests/core/test_auth.py::test_login

# Database migrations
cd backend && alembic upgrade head
cd backend && alembic revision --autogenerate -m "description"

# Code formatting
black backend/
```

### Frontend

```bash
# Install
cd frontend && npm install

# Run React tests
cd frontend && npm test

# Run Selenium browser tests (parallel)
pytest -n auto --dist loadgroup ./frontend/tests

# Build
cd frontend && npm run build
```

## Architecture

### Backend (`backend/app/`)

FastAPI app with modules organized by domain:

| Module | Purpose |
|--------|---------|
| `core/` | Auth (JWT), user management, settings |
| `data_tables/` | Core entities: Company, Job, Person, Interview, Location, Keyword |
| `job_email_scraping/` | Email/web scraping from Indeed, LinkedIn, NHS, VeganJobs |
| `job_rating/` | AI-powered job rating via OpenAI |
| `demo/` | Demo schema isolation — setup, seeding, cleanup |
| `payments/` | Stripe integration — checkout, webhooks, customer management |
| `emails/` | SMTP email service, release notes, templates |
| `service_runner/` | Background job scheduler |
| `routers/` | Export endpoints, misc config |

Key files:
- `main.py` — FastAPI app setup, CORS, middleware, all router registrations, lifespan hooks
- `database.py` — SQLAlchemy engines, `demo_mode` ContextVar, `get_db()` dependency
- `config.py` — Pydantic `Settings` class reading from `.env`
- `base_models.py` — `CommonBase` (id, created_at, modified_at) and `Owned` (adds owner_id with CASCADE delete)
- `models.py` — imports all models to ensure Alembic sees them

### Frontend (`frontend/src/`)

React + TypeScript app (Create React App):

- `App.tsx` — routing and top-level layout
- `components/DataModal/` — CRUD modals for each entity (Job, Company, Person, Interview, etc.)
- `components/DataTable/` — table views for each entity
- `services/` — API service layer (axios/fetch calls)
- `contexts/` — React context for shared state
- `hooks/` — custom React hooks
- `pages/` — page-level components

### Chrome Extension (`chrome-extension/`)

Manifest V3 extension for scraping LinkedIn job listings. Uses `content.js` for page injection and `popup.js` for the UI. Communicates with the JAM backend to save jobs.

### Database

PostgreSQL with two schemas:
- **public** — all real user data
- **demo** — isolated schema for demo users (created fresh per demo session)

Alembic manages migrations. Models in each domain module have their own `models.py`. All models inherit from `CommonBase` or `Owned`. `Base = declarative_base()` lives in `database.py`.

### Auth & Demo Mode

- JWT tokens via PyJWT. Tokens for demo users include an `is_demo` claim.
- HTTP middleware in `main.py` decodes JWTs and sets the `demo_mode` ContextVar.
- When `demo_mode` is set, `get_db()` returns a session on the `demo` engine (search_path=demo).
- Demo login: authenticates a real demo user → creates a temp user in the demo schema → seeds data → returns JWT with `is_demo=True`.
- Demo cleanup: `POST /demo/cleanup` deletes the temp user (cascade handles all owned data). Stale demo users (>24h) are cleaned up on startup.

### Background Scheduler

The scheduler runs on a **separate uvicorn process** (port 8001) with `SCHEDULER=true`. This prevents duplicate job execution when the API runs with multiple workers.

### Testing

- **Backend:** pytest + pytest-xdist (parallel), pytest-cov for coverage. Test fixtures in `tests/conftest.py`. Test data factories in `tests/utils/create_data/`.
- **Frontend:** Selenium browser automation via pytest. `frontend/tests/react_select.py` provides helpers for React Select interactions.
- CI runs both suites in parallel on GitHub Actions with a PostgreSQL 17 service container.

## Configuration

Backend reads from `backend/.env`. Key variable groups:
- `DB_*` — PostgreSQL connection
- `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` — JWT
- `SMTP_*`, `IMAP_*` — email (Hostinger)
- `OPENAI_API_KEY` — job rating
- `STRIPE_*` — payments
- `APIFY_*`, `BRIGHTDATA_*` — web scraping

Frontend reads from `frontend/.env` (typically just the API base URL).

## Code Style

- Python: Black formatter, 120-char line length
- TypeScript: Prettier (see `.prettierrc`), Stylelint for SCSS
- SCSS variables in `frontend/src/_variables.scss`, themes in `Themes.scss`