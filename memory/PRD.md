# Football PWA — PRD

## Original Problem Statement
Build a PWA for an 11-inch tablet for a 10-year-old kid with up-to-date news about European football matches (Premier League, Champions League, Portuguese League, etc.). News should include latest scores, statistics, and short stories. Use a free API service. App should have simple login for saving favorites. Kid-friendly design.

## User Persona
- 10-year-old kid on a tablet (11-inch)
- Wants scores, stats, and match stories
- Simple login to save favorite teams/leagues

## Core Requirements
- PWA with offline support
- European football leagues (PL, CL, PPL, PD, SA, BL1, FL1)
- Match scores, standings, top scorers
- Match detail modals (timeline, H2H, referee)
- Team profile pages
- Player detail modals
- Simple JWT auth for saving favorites
- Multi-language: EN, RU, PT
- Kid-friendly UI, tablet-optimized

## Architecture
```
/app/
├── backend/
│   ├── server.py (FastAPI, API proxy, MongoDB caching, Auth)
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── public/ (manifest.json, sw.js, custom icons)
│   ├── src/
│   │   ├── components/ (MatchCard, Navigation, MatchDetailModal, PlayerDetailModal, SettingsGear)
│   │   ├── contexts/ (AuthContext, LanguageContext)
│   │   ├── i18n/ (translations.js)
│   │   ├── pages/ (HomePage, LeaguePage, TeamPage, FavoritesPage, LoginPage)
│   │   ├── App.js, index.js, App.css, index.css
│   │   └── swRegistration.js
```

## What's Been Implemented

### Phase 1 — Foundation (done)
- App boilerplate, JWT Auth, MongoDB connection
- football-data.org API integration + caching layer
- PWA Service Worker, offline caching, custom icons
- Multi-language (EN/RU/PT) with settings gear

### Phase 2 — Leagues & Matches (done)
- League cards with official crests
- Standings table with W/D/L, GD, Pts
- Matches tab (upcoming + recent results)
- Top Scorers tab
- Match Detail Modal: score, HT, timeline, referee, venue
- H2H (Head-to-Head) stats with recent history

### Phase 3 — Teams & Players (done)
- Team Profile page (/team/:id) — stadium, coach, squad grouped by position
- Player Detail Modal — age, nationality, position, contract

### Phase 4 — Enriched Match Details & Season Progress (done — Apr 2026)
- Season Progress Bar on league pages (Matchday X / 38, % complete)
- Winner highlighting in MatchDetailModal (Trophy badge)
- Extra Time / Penalties badges with scores
- H2H total goals display ("17 goals in 5 meetings")
- H2H win/draw/loss stats bar

## Key Technical Details
- Frontend: React, TailwindCSS, Shadcn UI, PWA Service Worker
- Backend: FastAPI, PyJWT (cookie auth), HTTPX
- Database: MongoDB (caching + user favorites)
- API: football-data.org (free tier, 10 req/min, 5-30min cache)

## DB Schema
- `users`: {email, hashed_password, favorites: {leagues: [], teams: []}}
- `football_cache`: {url, response_data, timestamp}

## Key API Endpoints
- `/api/auth/login`, `/api/auth/register`, `/api/auth/me`
- `/api/leagues`, `/api/leagues/{code}/standings`
- `/api/leagues/{code}/matches`, `/api/leagues/{code}/scorers`
- `/api/leagues/{code}/season` (new — season progress)
- `/api/matches/{match_id}` (with H2H)
- `/api/teams/{team_id}`, `/api/players/{player_id}`
- `/api/favorites`

## Backlog

### P1 — Upcoming
- Dark mode toggle
- Push notifications for favorite team match alerts

### P2 — Future
- "Did you know?" fun facts (stadium, founded year)
- Penalty stats in top scorers list
- Global search for teams and players

## Known Issues / Notes
- Route ordering in server.py is critical: `/matches/today` MUST precede `/matches/{match_id}`
- Match Stories are generated programmatically (no news API in free tier)
- football-data.org free tier: 10 req/min limit, backend caches responses
- Response in Russian (user preference)
