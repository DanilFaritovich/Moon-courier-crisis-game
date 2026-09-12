# Moon Courier Crisis Game

[![CI](https://github.com/DanilFaritovich/Moon-courier-crisis-game/actions/workflows/ci.yml/badge.svg)](https://github.com/DanilFaritovich/Moon-courier-crisis-game/actions/workflows/ci.yml)

**Moon Courier Crisis** is a turn-based logistics game where the player
operates lunar rovers from a mission-control interface. The goal is to assign
rovers to delivery contracts, manage battery capacity, complete missions, and
plan the next turn.

It is a full-stack pet project built to demonstrate practical backend and
frontend engineering: a typed FastAPI API, domain-oriented game services, and
an interactive Vue 3 game UI.

## Interface preview

| Mission overview | Active delivery |
| --- | --- |
| ![Lunar map with contracts and rover dock](docs/images/mission-overview.png) | ![Assigned rover with updated battery and delivery status](docs/images/active-delivery.png) |

## Highlights

- Interactive SVG lunar map with pan and zoom.
- Drag a rover onto a destination to assign a contract.
- Contract selection when a destination has multiple available orders.
- Backend-calculated delivery feasibility and projected battery level.
- Delivery cancellation from rover cards and the Tactical Info panel.
- Turn processing that completes deliveries and generates new contracts.
- Strict TypeScript, component tests, linting, formatting, and GitHub Actions
  CI.

## Tech stack

| Area | Technologies |
| --- | --- |
| Frontend | Vue 3, TypeScript, Composition API, Vite |
| Frontend quality | Vitest, Vue Test Utils, ESLint, Prettier, `vue-tsc` |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| Backend quality | Pytest, Ruff, Mypy |
| Automation | GitHub Actions |

## Architecture

```text
Vue 3 game UI
      │  HTTP via the Vite development proxy
      ▼
FastAPI routers ──► GameService ──► domain services
      │                  │               ├── delivery service
      │                  │               ├── rover service
      │                  │               ├── order service
      │                  │               └── graph service
      ▼                  ▼
Pydantic response models   SQLAlchemy repositories / SQLite
```

The frontend keeps UI state locally and uses a small typed API client. Game
rules, path calculation, availability checks, battery calculation, and state
transitions remain on the backend rather than being duplicated in the browser.

## Key engineering decisions

- **Backend remains authoritative.** The UI never invents delivery outcomes:
  it requests the rover's available contracts and battery forecast from the
  API before confirmation.
- **Seeded playable state.** On startup, the backend seeds the map, starter
  rovers, and contracts. The game is immediately playable; the frontend does
  not need a separate initialization flow.
- **Focused components.** The game map, rover dock, tactical panel, contract
  picker, and confirmation dialog are separate Vue components.
- **Safe delivery lifecycle.** Creating or cancelling a delivery updates rover,
  order, and delivery state together through the game service.
- **Quality gate in CI.** Every pull request runs backend checks plus frontend
  formatting, linting, type checking, tests, and a production build.

## Running locally

### Prerequisites

- Python 3.14
- Node.js 22 and npm

Open two terminals in the repository root.

### Docker (recommended for a quick demo)

With Docker Desktop or Docker Engine running:

```bash
docker compose up --build
```

Open <http://127.0.0.1:8080>. Nginx serves the Vue application and proxies API
requests to FastAPI inside the Compose network. Stop the application with
`Ctrl+C`; add `--detach` to run it in the background.

The sections below describe running the frontend and backend separately for
development.

### 1. Start the backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

cd backend
uvicorn app.main:app --reload
```

The API runs on <http://127.0.0.1:8000>. FastAPI documentation is available at
<http://127.0.0.1:8000/docs>.

### 2. Start the frontend

```bash
cd frontend
npm ci
npm run dev
```

Open the address printed by Vite, normally <http://127.0.0.1:5173>. During
development, Vite proxies `/game` and `/health` requests to FastAPI.

## Gameplay

1. Drag an idle rover from the bottom dock to a map point with a contract.
2. If the point has several feasible contracts, choose one from the list.
3. Review the payload, reward, and predicted battery level, then confirm.
4. Click **Next Turn** to complete active deliveries and generate contracts.
5. An active delivery can be cancelled from the rover card or Tactical Info;
   the rover returns to base and the contract becomes available again.

## API overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | API health check |
| `GET` | `/game/state` | Current game state |
| `GET` | `/game/map` | Map points and roads |
| `GET` | `/game/rovers/{rover_id}/available-orders` | Feasible orders and battery projection |
| `POST` | `/game/deliveries` | Create a delivery (`rover_id`, `order_id`) |
| `DELETE` | `/game/deliveries/{delivery_id}` | Cancel a delivery |
| `POST` | `/game/next-turn` | Advance the simulation by one turn |

`POST /game/initialize` is retained for API compatibility. The frontend does
not call it because startup seeding makes the game ready automatically.

## Quality checks

### Backend

Run from the repository root with the virtual environment activated:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy .
python -m pytest
```

### Frontend

```bash
cd frontend
npm run format:check
npm run lint
npm run typecheck
npm run test
npm run build
```

The frontend test suite covers the API client, key UI components, contract
selection, delivery cancellation, and primary GameView workflows.

## Project structure

```text
.
├── backend/             # FastAPI application, domain services, models, tests
├── frontend/            # Vue 3 application and component tests
├── data/map.json        # Lunar map source data
├── .github/workflows/   # Backend and frontend CI
└── pyproject.toml       # Python tooling configuration
```

## Future improvements

- Add Playwright end-to-end coverage for browser-native drag and drop.
- Persist games in PostgreSQL instead of the current in-memory SQLite database.
- Add random events, road risk effects, and richer rover upgrades.
- Add save slots and player profiles.

## Current limitation

The project intentionally uses in-memory SQLite for a fast development setup.
Game state is scoped to one backend process and resets when that process is
restarted.
