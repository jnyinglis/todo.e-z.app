# Repository Guidelines

## Project Structure & Module Organization
- `frontend/` — Vite + React + TypeScript app (assets in `public/`, source in `src/`).
- `backend/` — FastAPI app (`app/api`, `app/core`, `app/models`, `app/schemas`; entry `main.py`).
- `data/` — local Postgres volume (dev).
- `docker-compose.dev.yml` / `docker-compose.prod.yml` — local vs production stacks.
- `scripts/` — setup and utility scripts.

## Build, Test, and Development Commands
- `make dev` — start full stack (frontend, backend, db) with hot reload.
- `make dev-build` — rebuild containers and start dev stack.
- `make prod` — run production stack (Traefik, backend, frontend, db).
- `make test` | `make test-backend` — run all tests or backend tests (`pytest`).
- `make lint` | `make type-check` — ESLint (frontend) and mypy/pytest checks (backend).
- `make migrate` — run Alembic migrations; `make logs` — follow dev logs.

Examples:
- `pnpm dev` (root) mirrors `make dev`; `pnpm test:backend` runs `pytest`.
- `docker-compose -f docker-compose.dev.yml up --build` for one-off rebuilds.

## Coding Style & Naming Conventions
- Frontend: TypeScript, 2-space indent. ESLint configured in `frontend/eslint.config.js`.
  - Components: `PascalCase` in `src/components/`; pages in `src/pages/`.
- Backend: Python, 4-space indent; type hints required. Routers in `app/api/*`, Pydantic models in `app/schemas/*`, SQLAlchemy models in `app/models/*`.
- Keep modules small and cohesive; prefer pure functions and typed interfaces/schemas.

## Testing Guidelines
- Backend: `pytest` (+ `pytest-asyncio`, `httpx`); name tests `tests/test_*.py`.
  - Aim for coverage of routers, services, and schema validation.
- Frontend: Add tests under `src/__tests__/` (if added, use Vitest/JSDOM). Snapshot UI sparingly.
- Run: `make test` or `pnpm test:backend`.

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- PRs must include: clear description, linked issues, test plan, and UI screenshots for visible changes.
- Keep PRs focused; ensure `make type-check` and `make lint` pass.

## Security & Configuration
- Never commit secrets. Copy envs via `cp .env.example .env` and adjust locally.
- Local DB URL is provided via Compose; backend uses `DATABASE_URL`/`DATABASE_URL_SYNC`.
- CORS: frontend dev runs on `http://localhost:5173`; update if needed.
