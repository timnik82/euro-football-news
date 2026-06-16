# Repository Guidelines

## Project Structure & Module Organization

This repository contains a football news application with a Python FastAPI backend and a React frontend.

- `backend/` contains API code, configuration, database access, services, and routers.
- `backend/routers/` groups API routes by feature, such as auth, football, favorites, gamification, and admin diagnostics.
- `backend/tests/` contains backend pytest coverage for API and regression behavior.
- `frontend/` contains the CRACO/Create React App client.
- `frontend/src/pages/`, `frontend/src/components/`, `frontend/src/hooks/`, and `frontend/src/contexts/` hold page views, reusable UI, hooks, and app state.
- `frontend/public/` stores static app assets. `test_reports/` stores generated screenshots and pytest XML reports.

## Build, Test, and Development Commands

Run backend commands from `backend/`:

- `pip install -r requirements.txt` installs Python dependencies.
- `uvicorn server:app --reload` starts the FastAPI server for local development.
- `python -m pytest tests` runs backend tests.

Run frontend commands from `frontend/`:

- `npm install` installs frontend dependencies.
- `npm start` starts the React dev server at `http://localhost:3000`.
- `npm test -- --watchAll=false` runs frontend tests once.
- `npm run build` creates a production build.

Before committing, run `npm test -- --run` and `npm run build` when frontend changes are involved.

## Coding Style & Naming Conventions

Python code uses 4-space indentation and snake_case names for functions, variables, and modules. Keep route handlers thin and put shared business logic in service modules such as `football_service.py` or `match_story_service.py`.

Frontend code uses JavaScript/JSX, PascalCase component files, camelCase hooks/utilities, and the `@/` import alias. Prefer existing UI components in `frontend/src/components/ui/` and Tailwind utility classes already used in the app.

## Testing Guidelines

Backend tests use pytest and follow `test_*.py` naming. Add focused tests in `backend/tests/` for API changes, regressions, auth behavior, and story/gamification logic. Keep generated evidence, screenshots, and reports under `test_reports/` rather than mixing them into source folders.

## Commit & Pull Request Guidelines

Recent history uses automated commit messages, so use clear imperative messages for new work, for example `Add match story diagnostics test`. Prefer flat branch names such as `codex-football-news-fix`.

Pull requests should include a short summary, tests run, linked issues when applicable, and screenshots for visible UI changes. Use explicit staging paths and avoid committing unrelated generated files.

## Security & Configuration Tips

Backend configuration is loaded from `backend/.env`. Do not commit secrets such as `FOOTBALL_API_KEY`, JWT secrets, database URLs, or service credentials. Document required environment variables when adding new integrations.
