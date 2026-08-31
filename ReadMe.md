<p align="center">
  <img src="https://github.com/Emmanuelpean/jam/blob/main/frontend/src/assets/Logo_color.svg" alt="Jam" width="150">
</p>

<h1 align="center">JAM</h1>
<h2 align="center">Job Application Manager</h2>

<div align="center">

  [![Test and Deploy](https://github.com/Emmanuelpean/jam/actions/workflows/test.yml/badge.svg)](https://github.com/Emmanuelpean/jam/actions/workflows/test.yml)
  [![Tests Status](./reports/tests/tests-badge.svg?dummy=8484744)](https://emmanuelpean.github.io/jam/reports/tests/report.html?sort=result)
  [![Coverage Status](./reports/coverage/coverage-badge.svg?dummy=8484744)](https://emmanuelpean.github.io/jam/reports/coverage/htmlcov/index.html)
  [![Last Commit](https://img.shields.io/github/last-commit/emmanuelpean/jam?branch=main)](https://github.com/emmanuelpean/jam/commits?branch=main)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>

*Jam* is a user-friendly web app designed to help you manage your jobs, Applications, Interviews, and everything in-between.
job search can be a time-consuming and tedious process, requiring to keep track of many jobs and applications at the same time. 
*Jam* aims to make this process easier so that you can get the job of your dreams. *Jam* can:
<li>Create and manage job application records</li>
<li>Track interview schedules and outcomes</li>
<li>Store company and contact information</li>
<li>Monitor application status, progress, and deadline</li>

## Prerequisites

| Requirement | Version | Notes                                        |
|-------------|---------|----------------------------------------------|
| Python      | ≥ 3.12  |                                              |
| Node.js     | ≥ 20    | with npm                                     |
| PostgreSQL  | 17      | running locally and reachable on port 5432   |
| Chrome      | latest  | only needed to run the Selenium test suites  |

## Setup

### 1. Clone and create a virtual environment

```console
$ git clone https://github.com/Emmanuelpean/jam.git
$ cd jam
$ python -m venv .venv
$ .venv\Scripts\activate          # Windows
$ source .venv/bin/activate       # macOS / Linux
```

### 2. Install dependencies

```console
$ pip install -e "./backend[dev]"
$ cd frontend && npm install && cd ..
$ cd chrome_extension && npm install && cd ..   # optional, only for the Chrome extension
```

### 3. Create the database

Create an empty PostgreSQL database (the tables are created in the next step):

```console
$ createdb -U postgres jam
```

Or from `psql`:

```sql
CREATE DATABASE jam;
```

The `demo` schema used by demo accounts is **not** created manually — the backend drops and recreates it
on every startup.

### 4. Create the environment files

Both `.env` files are gitignored and must be created from the provided templates:

```console
$ cp backend/example.env backend/.env
$ cp frontend/example.env frontend/.env
```

Then edit `backend/.env`:

- **`DATABASE_*`** — match the PostgreSQL instance and the database created above.
- **`SECRET_KEY`** — generate one with `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
- **`LOG_DIRECTORY`** — absolute path to an existing, writable directory (e.g. `<repo>/logs`).
- **Third-party keys** (`ANTHROPIC_*`, `OPENAI_*`, `APIFY_*`, `BRIGHTDATA_*`, `STRIPE_*`, `TURNSTILE_*`,
  `*_EMAIL_PASSWORD`) — every variable must be present or the app will not start, but dummy placeholder
  values are fine for local development. Only the features that call out to a given provider
  (AI job rating, job scraping, payments, captcha, transactional email) will fail.

`frontend/.env` works as-is for the default local ports.

### 5. Create the tables

Starting the app does **not** create them: the only `create_all` that runs at startup targets the `demo`
schema, so the public schema has to be built explicitly. Pick one of:

```console
$ cd backend && python -m tests.utils.create_tables   # empty schema
$ cd backend && python -m tests.utils.seed_database   # sample data (drops all existing tables)
```

`create_tables` creates every table from the models, inserts nothing, and stamps the database at the
Alembic head so later `alembic upgrade head` calls apply only the new migrations. It creates only the
tables that are missing and never drops anything, so it is safe to re-run.

`seed_database` drops everything, rebuilds from the models, fills the tables with sample data, and
stamps the head the same way. It contains ready-to-use accounts, including `regular@example.com` /
`password1` and the admin account `admin@example.com` / `password2`.

## Usage

To run the app locally, run:
```console
$ ./run.bat          # Windows
$ ./run.sh           # macOS / Linux
```

Either script opens three terminals:

| Process        | Port | Command                                                          |
|----------------|------|------------------------------------------------------------------|
| Frontend       | 3000 | `npm start` (from `frontend/`)                                   |
| Backend API    | 8000 | `uvicorn app.main:app --reload --port 8000` (from `backend/`)    |
| Scheduler      | 8001 | same, with `SCHEDULER=true`                                      |

The app is then available at http://localhost:3000/jam, and the API docs at http://localhost:8000/docs.

The scheduler runs the background services (scraping, rating, monitoring) and must run as a separate
process so the jobs are not executed once per API worker.

## Chrome extension

```console
$ cd chrome_extension
$ npm install
$ npm run build
```

Then load `chrome_extension/dist` as an unpacked extension from `chrome://extensions` with developer
mode enabled.

## Testing

```console
$ pytest -n auto ./backend                          # backend tests
$ pytest -n auto --dist loadgroup ./frontend/tests  # frontend Selenium tests
$ pytest ./chrome_extension/tests                   # extension Selenium tests
```

The backend suite creates and drops its own `jam_test*` databases, so the PostgreSQL user in
`backend/.env` needs the `CREATEDB` privilege.

## Code style

```console
$ black backend/          # Python, 120-char lines
$ cd frontend && npx prettier --write src/
```

## Database migrations

```console
$ cd backend && alembic revision --autogenerate -m "description"
$ cd backend && alembic upgrade head
$ cd backend && alembic current              # revision the database is on
$ cd backend && alembic check                # report models not covered by a migration
```

The chain is replay-tested. `backend/tests/test_migrations.py` applies
`backend/tests/utils/baseline_schema.sql` - the schema as it stood at commit `86ea019d~1`, just before
the first migration was written - then runs every revision up to head, back down to base and up again,
and asserts the result is identical to the models. A migration that leaves the schema out of step with
the models, or a `downgrade()` that is not a working inverse, fails that test.
