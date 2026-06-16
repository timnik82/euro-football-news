# Deployment Research: Moving Goal Kick Off Emergent

Research date: June 16, 2026

This guide explains how to deploy this Emergent-generated football news app somewhere cheaper and more controllable than Emergent. It is written for a technical owner who is comfortable with tools and dashboards, but does not want to spend days learning cloud infrastructure.

## Short Recommendation

Because you already have a premium Railway plan, the best first choice is:

1. Deploy the backend on Railway.
2. Deploy the frontend on Railway.
3. Add MongoDB inside the same Railway project.
4. Use Railway public domains first, then add a custom domain after the app works.

This keeps the whole application in one place: code services, database, environment variables, logs, metrics, domains, and redeploys. That is simpler than splitting the app across several platforms.

Recommended ranking:

| Rank | Option | Best For | Why |
| --- | --- | --- | --- |
| 1 | Railway backend + Railway frontend + Railway MongoDB | Your current situation | You already pay for Railway, and Railway supports FastAPI, React, MongoDB templates, env vars, logs, and domains. |
| 2 | Railway backend/frontend + MongoDB Atlas | Safer database operations | Atlas is a dedicated managed MongoDB service with a free M0 tier and stronger database-focused tooling. |
| 3 | Render backend/static frontend + MongoDB Atlas | Fallback if Railway is awkward | Render has clear web service and static site flows, but you already have Railway. |
| 4 | Zeabur or Kuberns | Emergent-specific migration help | Both publish Emergent migration/deployment guidance, but they add another platform to learn. |
| 5 | Vercel or Netlify alone | Frontend-only hosting | Not enough by itself, because this app also needs FastAPI and MongoDB. |

## What This App Needs To Run

This repository is a full-stack app, not just a static website.

| Part | Current Tech | Folder | Notes |
| --- | --- | --- | --- |
| Frontend | React, CRACO, Tailwind, PWA service worker | `frontend` | Builds into static files with `npm run build`. |
| Backend | FastAPI, Uvicorn, Motor async MongoDB driver | `backend` | Serves API routes under `/api`. |
| Database | MongoDB | external service | Stores users, favorites, cache, quiz attempts, match stories, and login lockouts. |
| External API | football-data.org | backend env var | Uses `FOOTBALL_API_KEY`. |

Emergent's own deployment tutorial says Emergent deployment costs 50 credits per month per deployed app, creates a public URL, supports environment variables, custom domains, managed infrastructure, redeploys, rollbacks, and shutdowns. The goal here is to keep the app live without paying Emergent's recurring deployment cost.

## Required Environment Variables

Do not commit real values for these. Add them in the deployment platform dashboard.

### Backend

| Variable | Required | What It Does |
| --- | --- | --- |
| `FOOTBALL_API_KEY` | Yes | API key for football-data.org. The backend will crash at startup if this is missing. |
| `MONGO_URL` | Yes | MongoDB connection string. Railway MongoDB exposes this name automatically. |
| `DB_NAME` | Yes | MongoDB database name, for example `goal_kick`. |
| `CORS_ORIGINS` | Yes | Comma-separated frontend URLs allowed to call the API with cookies. |
| `JWT_SECRET` | Yes | Secret used to sign login tokens. Use a long random value. |
| `ADMIN_EMAIL` | Yes | Admin account email to seed on startup. |
| `ADMIN_PASSWORD` | Yes | Admin account password to seed/update on startup. |

### Frontend

| Variable | Required | What It Does |
| --- | --- | --- |
| `REACT_APP_BACKEND_URL` | Yes | Public backend base URL, for example `https://goal-kick-backend.up.railway.app`. Do not include `/api`; the code adds `/api` itself. |

## Recommended Path: Railway

Create one Railway project with three services:

- `goal-kick-backend`
- `goal-kick-frontend`
- `mongodb`

This keeps service-to-service wiring easier. It also lets the backend use Railway's internal MongoDB connection variable instead of exposing the database publicly.

### 1. Put The Code On GitHub

Railway works best when it can deploy from a GitHub repository.

If this repo is not already on GitHub:

```bash
git init
git add backend frontend README.md AGENTS.md auth_testing.md backend_test.py design_guidelines.json test_result.md
git commit -m "Prepare Goal Kick for external deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Adjust the `git add` list if your repo has changed. The important rule is to stage the files you actually want to deploy, not local secrets or unrelated generated files. Do not commit `backend/.env`, `frontend/.env`, API keys, database passwords, or admin passwords.

### 2. Create The Railway Project

In Railway:

1. Click `New Project`.
2. Choose `Deploy from GitHub repo`.
3. Select this repository.
4. Add separate services for backend, frontend, and MongoDB.

Railway's FastAPI guide says it supports FastAPI deployment from a template, GitHub repository, CLI, or Dockerfile. For this app, GitHub is the cleanest route.

### 3. Add MongoDB

In the same Railway project:

1. Click `+ New`.
2. Choose the MongoDB database template.
3. Let Railway create the MongoDB service.
4. In the backend service, reference the MongoDB service's `MONGO_URL`.

Railway's MongoDB docs say the MongoDB template exposes:

- `MONGOHOST`
- `MONGOPORT`
- `MONGOUSER`
- `MONGOPASSWORD`
- `MONGO_URL`

That is good news because this backend already expects `MONGO_URL`.

Important: Railway MongoDB is convenient, but it is a template/container service. Before relying on it for important real user data, configure backups and understand restore steps. If you want the safest database path, use MongoDB Atlas instead.

### 4. Deploy The Backend

Create or configure the backend service like this:

| Setting | Value |
| --- | --- |
| Root directory | `backend` |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn server:app --host 0.0.0.0 --port $PORT` |
| Public networking | Enabled |

Add backend environment variables:

```text
FOOTBALL_API_KEY=<your football-data.org key>
MONGO_URL=${{mongodb.MONGO_URL}}
DB_NAME=goal_kick
CORS_ORIGINS=https://YOUR_FRONTEND_DOMAIN
JWT_SECRET=<long random secret>
ADMIN_EMAIL=<your admin email>
ADMIN_PASSWORD=<your admin password>
COOKIE_SECURE=true
COOKIE_SAMESITE=none
```

Set `COOKIE_SECURE=true` and `COOKIE_SAMESITE=none` whenever the frontend and backend are on different domains (the normal Railway case). See "Auth Cookies" under Production Risks for why this is required.

After the backend deploys, open:

```text
https://YOUR_BACKEND_DOMAIN/docs
```

You should see the FastAPI interactive API docs. If this page loads, the backend process is running.

### 5. Deploy The Frontend

Create or configure the frontend service like this:

| Setting | Value |
| --- | --- |
| Root directory | `frontend` |
| Build command | `npm install && npm run build` |
| Output directory | `build` |
| Public networking | Enabled |

Set this frontend environment variable:

```text
REACT_APP_BACKEND_URL=https://YOUR_BACKEND_DOMAIN
```

Do not add `/api` to this value. The frontend code already uses:

```js
`${process.env.REACT_APP_BACKEND_URL}/api`
```

If Railway does not automatically serve the React build output, add a simple static server. One common approach is:

```bash
npm install serve
```

Then use this start command:

```bash
npx serve -s build -l $PORT
```

If you make that change permanently, add `serve` to `frontend/package.json` so Railway can install it consistently.

### 6. Wire CORS Correctly

After Railway gives the frontend a public URL, update the backend `CORS_ORIGINS` value:

```text
CORS_ORIGINS=https://YOUR_FRONTEND_DOMAIN
```

For local and production testing together, use comma-separated values:

```text
CORS_ORIGINS=http://localhost:3000,https://YOUR_FRONTEND_DOMAIN
```

Because this app uses cookie-based login, exact domains matter. A typo here can make login appear broken even when the backend is healthy.

### 7. Smoke Test The App

Use this checklist after the first deploy:

- Open the frontend public URL.
- Open the backend `/docs` URL.
- Register a new test user.
- Log out and log back in.
- Add a favorite team or league.
- Open the games page.
- Open a league page and a team page.
- Temporarily refresh the app on a tablet-sized screen.
- Check Railway backend logs for startup errors.
- Check Railway frontend logs for build errors.

## Alternative: Railway + MongoDB Atlas

Use this if you want the database to be managed by MongoDB specialists rather than running a MongoDB container in Railway.

MongoDB Atlas has an M0 free tier with 512 MB storage. That is enough for a small family/personal football app and early testing. If the app becomes important or grows, upgrade the Atlas cluster.

Setup shape:

- Backend on Railway.
- Frontend on Railway.
- MongoDB on Atlas.
- `MONGO_URL` in Railway points to the Atlas connection string.
- In Atlas, allow Railway outbound access. The simplest first test is allowing all IPs, then tightening later if you choose a static outbound IP option.

This option is a little more setup, but safer for long-term database operations.

## Fallback: Render + MongoDB Atlas

Render is a reasonable fallback if Railway causes friction.

Render supports:

- Web services for Python/FastAPI-style backends.
- Static sites for React-style frontends.
- Git-based deploys.
- Environment variables.
- Custom domains and managed TLS.

For this app, the Render setup would be:

| Service | Platform | Notes |
| --- | --- | --- |
| Backend | Render Web Service | Root `backend`, build `pip install -r requirements.txt`, start `uvicorn server:app --host 0.0.0.0 --port $PORT`. |
| Frontend | Render Static Site | Root `frontend`, build `npm install && npm run build`, publish `build`. |
| Database | MongoDB Atlas | Use Atlas connection string as `MONGO_URL`. |

Render is not the first recommendation here only because you already have a Railway premium plan.

## Emergent-Specific Alternatives

### Zeabur

Zeabur has a direct "Import from Emergent" guide. It describes downloading or syncing the Emergent code, opening it locally, and using Zeabur's tooling to deploy. It also specifically mentions connecting MongoDB for apps that save user data.

Use Zeabur if you want a migration flow written specifically for Emergent-style projects.

### Kuberns

Kuberns has a 2026 guide for deploying Emergent apps to production. The article recommends exporting the code to GitHub, identifying environment variables, choosing a deployment platform that handles SSL, databases, and auto-restart, then deploying from GitHub.

Use Kuberns if you want an AI-assisted production deploy platform. I would still try Railway first because you already pay for it.

## Why Vercel Or Netlify Alone Is Not Enough

Vercel and Netlify are excellent for frontend deployments. They are not the cleanest full solution for this app because:

- This app has a persistent FastAPI backend.
- It uses MongoDB.
- It uses cookie-based auth.
- It expects a normal long-running API server.

You could use Vercel or Netlify for only the frontend, then host the backend on Railway. But if both frontend and backend can run well on Railway, keeping them together is simpler.

## Production Risks To Fix Or Test

### 1. Auth Cookies Must Be Configured For Cross-Site Production (Required)

This is a guaranteed login failure on Railway if not handled, not an optional follow-up. The frontend calls the API with `withCredentials: true`, and on Railway the frontend and backend get **different** subdomains (`*-frontend.up.railway.app` vs `*-backend.up.railway.app`) — a cross-site context. A `SameSite=Lax` cookie is **not** sent on cross-site XHR, so login appears to succeed (the `Set-Cookie` returns) but the next `/auth/me` carries no cookie and auth is silently broken.

Cookie behavior is now driven by environment variables (`COOKIE_SECURE`, `COOKIE_SAMESITE`) read in `backend/config.py` and applied in `backend/auth_service.py` and `backend/routers/auth.py`. Defaults (`secure=false`, `samesite=lax`) keep local HTTP development working.

For a Railway deploy with frontend and backend on different domains, set on the backend:

```text
COOKIE_SECURE=true
COOKIE_SAMESITE=none
```

`SameSite=None` is rejected by browsers unless `Secure` is also set, so both are required together. Alternatively, put the frontend and backend on the **same** domain (custom domain with path routing, or serve the React build from FastAPI); then the default `SameSite=Lax` works and you can leave these unset. Always test login in the real deployed domain, not only locally.

### 2. CORS Must Match The Frontend URL

The backend reads `CORS_ORIGINS` from the environment. If this does not include the exact frontend domain, browser requests may fail.

Example:

```text
CORS_ORIGINS=https://goal-kick-frontend.up.railway.app
```

If you later add a custom domain, add that too.

### 3. Test Credentials File Write (Now Disabled By Default)

On startup, `write_test_credentials_file()` used to write the admin email and password in plaintext to `/app/memory/test_credentials.md`, a path inherited from the Emergent environment. That was both a security smell (plaintext credentials on disk) and a potential startup crash on a read-only or absent path.

This is now opt-in and crash-safe: the write only happens when `WRITE_TEST_CREDENTIALS=true`, the target path is overridable with `TEST_CREDENTIALS_PATH`, and any filesystem error is logged instead of crashing startup. Leave `WRITE_TEST_CREDENTIALS` unset in production.

### 4. Emergent Visual Editing Dependency May Be Unavailable

The frontend has this dev dependency:

```text
@emergentbase/visual-edits
```

It is loaded only during the dev server path in `craco.config.js`, and the code already catches a missing module for local development. Production builds do not need Emergent visual editing.

This package has been removed from `frontend/package.json`; the `craco.config.js` dev-only loader already catches its absence, so the build is unaffected.

### 5. Emergent Backend Package Removed From requirements.txt

`backend/requirements.txt` previously pinned `emergentintegrations==0.1.0`, an Emergent-specific package that is not on public PyPI and would make `pip install -r requirements.txt` fail on Railway. It was imported nowhere in the code and has been removed. The file was also slimmed from a 130-package freeze (which dragged in unused libraries like pandas, numpy, boto3, google-genai, stripe, and huggingface) down to the actual direct dependencies; pip resolves the transitive packages. This was verified by a clean install plus an app import smoke test. Faster, lighter builds with no functional change.

### 6. Check Prices Again Before Paying

Pricing and plan terms change. This research was done on June 16, 2026. Before committing to a paid setup, recheck:

- Railway plan and usage pricing.
- MongoDB Atlas free and paid limits.
- Render fallback pricing.
- Any bandwidth or egress charges.

## Practical Click Checklist

Here is the shortest practical path.

1. Push the repo to GitHub.
2. Open Railway.
3. Create a new project from the GitHub repo.
4. Create a backend service from `backend`.
5. Add backend build/start commands.
6. Add backend environment variables.
7. Add a MongoDB service in the same Railway project.
8. Connect backend `MONGO_URL` to Railway MongoDB's `MONGO_URL`.
9. Generate a public domain for the backend.
10. Confirm `/docs` works on the backend URL.
11. Create a frontend service from `frontend`.
12. Add frontend build settings.
13. Set `REACT_APP_BACKEND_URL` to the backend URL.
14. Generate a public domain for the frontend.
15. Add the frontend domain to backend `CORS_ORIGINS`.
16. Redeploy backend and frontend.
17. Test login, favorites, league pages, team pages, and games.
18. Add a custom domain only after the Railway domains work.

## Sources

- [Railway FastAPI guide](https://docs.railway.com/guides/fastapi)
- [Railway React guide](https://docs.railway.com/guides/react)
- [Railway MongoDB docs](https://docs.railway.com/databases/mongodb)
- [Railway pricing plans](https://docs.railway.com/pricing/plans)
- [Emergent deployment tutorial](https://emergent.sh/tutorials/how-to-deploy-your-app-on-emergent)
- [Zeabur Import from Emergent](https://zeabur.com/docs/en-US/get-started/migration/emergent)
- [Kuberns Emergent deployment guide](https://kuberns.com/blogs/deploy-emergent-app-to-production/)
- [MongoDB Atlas pricing](https://www.mongodb.com/pricing)
- [Render Web Services](https://render.com/docs/web-services)
- [Render Static Sites](https://render.com/docs/static-sites)
