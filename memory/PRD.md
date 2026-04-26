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

### Phase 5 — Global Search (done — Apr 2026)
- Search icon in bottom navigation bar
- Full-screen search overlay (SearchModal.js)
- Search teams by name → navigates to team profile page
- Search players (from scorers cache) → shows goals count, opens PlayerDetailModal
- Debounced input (350ms), results panel with TEAMS / PLAYERS sections
- Backend `/api/search?q={query}` searches across all 7 leagues from cache

### Phase 6 — App Icon Refresh (done — Apr 2026)
- Replaced favicon and PWA app icons with the user-provided `gemini-svg.svg`
- Regenerated `favicon.ico`, `logo192.png`, `logo512.png`, and `apple-touch-icon.png`
- Verified that the preview serves the updated icon assets correctly

### Phase 7 — iPad Safari Splash Polish (done — Apr 2026)
- Added iPad-specific Apple touch icon (`167x167`) for installed PWA on Safari
- Created custom startup splash images for iPad 10.9 in portrait and landscape
- Updated `public/index.html` with Apple startup image links for iPad Safari installation flow

### Phase 8 — In-App Brand Header Polish (done — Apr 2026)
- Added a shared `BrandHeading` component using the custom app icon and `Goal Kick` wordmark
- Placed brand heading on homepage, leagues, league detail, team page, favorites, and login screen
- Verified the branded header renders correctly across the main navigation flow

### Phase 9 — Homepage Content Simplification (done — Apr 2026)
- Reordered homepage sections so match stories appear before upcoming matches
- Removed league pills and league explore cards from the homepage to reduce duplication with the Leagues tab
- Verified homepage now focuses on stories first, then the nearest matches

### Phase 10 — Smarter Match Story Localization (done — Apr 2026)
- Replaced repetitive homepage match-story phrasing with rule-based summaries driven by scoreline patterns
- Added lighter, more natural story variants for English, Russian, and Portuguese
- Kept a safe fallback so homepage stories still render cleanly when detailed match context is limited

### Phase 11 — Homepage Story Card Cleanup (done — Apr 2026)
- Removed the lower descriptive paragraph from homepage match-story cards
- Kept the API-driven essentials visible: competition, teams, crests, and score
- Verified that only the extra description disappeared while the rest of the card stayed intact

### Phase 12 — Code Hygiene Refactor (done — Feb 2026)
- Filled missing `player.*` translations in Russian (RU) — was falling back to English
- Removed duplicated PT `settings` key created during translation patching
- Centralized league metadata (name, country, color, emblem) into `frontend/src/constants/leagues.js`; `LeaguePage.js` now reads from a single source instead of three local hardcoded maps
- Dropped dead English headline/summary generator from backend `/api/stories` (frontend already localizes via `localizeStory`); endpoint now returns minimal payload (match_id, teams, score, competition, date, matchday)
- Backend dropped from 657 → 626 lines; LeaguePage from 368 → 352 lines

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

## Known Issues / Notes
- Route ordering in server.py is critical: `/matches/today` MUST precede `/matches/{match_id}`
- Match Stories are generated programmatically (no news API in free tier)
- football-data.org free tier: 10 req/min limit, backend caches responses
- Response in Russian (user preference)
