# Cricket Live Dashboard

A real-time cricket match dashboard that automatically refreshes itself on a schedule, backed by PostgreSQL, built with Plotly Dash, and fully containerized with Docker.

## Architecture

```
CricAPI  →  Python refresh job (every 5 min)  →  PostgreSQL (live_matches)
                                                          ↓
                                          Plotly Dash app  →  Browser (localhost:8050)

All wrapped in Docker Compose (dashboard container + postgres container)
```

## What it does

1. **Fetch**: Pulls live match data (teams, venues, status, scores) from the [CricAPI](https://www.cricapi.com/) public API
2. **Store**: Upserts records into a PostgreSQL table (`live_matches`) — new matches are inserted, existing ones are updated in place rather than duplicated
3. **Schedule**: An APScheduler background job re-runs the fetch-and-store step automatically every 5 minutes, with no manual intervention
4. **Display**: A Plotly Dash web app queries PostgreSQL and renders a live bar chart (matches by venue) and a sortable match table, both auto-refreshing every 30 seconds in the browser
5. **Containerize**: The entire stack (dashboard app + PostgreSQL) runs via Docker Compose — one command spins up both services, networked together, portable to any machine with Docker installed

## Tech stack

- **Language**: Python 3.12
- **Database**: PostgreSQL 16
- **Web framework**: Plotly Dash
- **Scheduling**: APScheduler (BackgroundScheduler)
- **Containerization**: Docker, Docker Compose
- **Data source**: CricAPI (REST API)

## Key engineering decisions

- **Upsert over append**: Unlike a pure logging table, `live_matches` uses `ON CONFLICT (match_id) DO UPDATE` so the table always reflects current match state rather than accumulating duplicate rows across refresh cycles.
- **Self-initializing schema**: The app creates its own `live_matches` table on startup if it doesn't exist (`CREATE TABLE IF NOT EXISTS`), so a fresh container with an empty database initializes itself correctly with zero manual setup steps — critical for genuine portability.
- **Host binding for containers**: The Dash server binds to `0.0.0.0` rather than `127.0.0.1` inside the container — `127.0.0.1` only accepts connections from inside the container itself, which would make the app unreachable from the host machine's browser despite correct port mapping.
- **Separate database container**: PostgreSQL runs as its own Docker service rather than embedded in the app container, mirroring how this would actually be deployed (independently scalable, independently restartable, data persisted via a named volume even if the app container is rebuilt).
- **`.dockerignore` for build performance and correctness**: Excludes the local Python virtual environment from the Docker build context — without this, Windows-specific compiled binaries (e.g. `pyarrow` `.dll` files from a Windows venv) get copied into the Linux container, causing multi-minute build times and image corruption errors.

## Project structure

```
cricket-live-dashboard/
├── scheduled_dashboard.py     # Main entry point: Dash app + APScheduler + table init
├── dashboard_app.py           # Standalone Dash app (manual refresh, no scheduler)
├── refresh_dashboard_data.py  # Fetch (CricAPI) + upsert (PostgreSQL) logic
├── setup_postgres.py          # One-time table creation script
├── test_postgres.py           # Standalone PostgreSQL connectivity check
├── Dockerfile                 # Container image definition for the dashboard app
├── docker-compose.yml         # Orchestrates dashboard + postgres containers together
├── requirements.txt           # Python dependencies
├── .dockerignore               # Excludes venv/ and other host-only files from the image
└── .env                        # API key and DB password (not committed)
```

## Running it locally

### Option A: Docker (recommended — matches production setup)

```bash
# Set up your .env file with CRICAPI_KEY and POSTGRES_PASSWORD

docker compose build
docker compose up
```

Then open `http://localhost:8050` in your browser.

### Option B: Native Python (without Docker)

```bash
pip install -r requirements.txt

# Requires a local PostgreSQL instance running on port 5432
python scheduled_dashboard.py
```

## Future improvements

- Add a "last N matches" historical view instead of only current matches
- Add basic authentication if deployed publicly
- Move scheduling interval to an environment variable instead of a hardcoded value
- Add health check endpoints for container orchestration platforms (Kubernetes, ECS)
