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
│   ├── server.py (FastAPI app assembly, CORS, startup indexes)
│   ├── config.py, database.py, schemas.py
│   ├── auth_service.py, football_service.py, gamification_service.py
│   ├── match_story_utils.py, match_story_sources.py, match_story_builder.py, match_story_service.py
│   ├── routers/ (auth.py, football.py aggregate, leagues.py, teams.py, matches.py, stories.py, search.py, gamification.py, favorites.py)
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── public/ (manifest.json, sw.js, custom icons)
│   ├── src/
│   │   ├── components/ (MatchCard, MatchDetailModal, MatchStorySection, PlayerDetailModal, SearchModal, SettingsGear)
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

### Phase 13 — "Next Favorite Match" Hero on Homepage (done — Feb 2026)
- Added `NextFavoriteMatchHero` component: gradient hero card showing the soonest upcoming match for any of the user's favorite teams
- Live countdown (days/hours/minutes/seconds) updating every second
- Shows favorite team's crest + name with HOME/AWAY label and opponent
- Click opens existing `MatchDetailModal`
- Added EN/RU/PT translations under `nextMatch.*`
- HomePage now also fetches user favorites (when logged in) alongside today/upcoming/stories

### Phase 14 — Match-specific Educational "Story of the Match" (done — Apr 2026)
- Added backend endpoint `/api/matches/{match_id}/story?lang=en|ru|pt`
- Story flow checks MongoDB `match_stories` cache first, then searches configured news providers, normalizes article responses, scores match relevance, and saves the final processed story
- Integrated GNews, NewsData.io, and NewsAPI.org provider adapters via backend-only environment variables
- Added child-friendly fallback story generation from exact match data when no relevant external article is available
- Added `MatchStorySection` inside `MatchDetailModal` with loading, fallback, image, source links, optional video link, and key points
- Added EN/RU/PT UI translations under `matchStory.*`
- Added backend regression tests in `/app/backend/tests/test_match_story_api.py`

### Phase 15 — News Provider Retry & Relevance Hardening (done — Apr 2026)
- Re-tested NewsAPI key using both query-param and `X-Api-Key` header methods; provider still returns 401 invalid key
- Improved provider search to use English source search regardless of UI language, while keeping generated story output localized EN/RU/PT
- Improved match queries to prefer short team names and try exact score/highlights/report variants
- Fixed NewsData date parsing bug for naive timestamps that could interrupt relevance scoring
- Added stricter article filtering to reject transfer/scouting/lineup/prediction/betting-style results that are not true match stories
- Bumped match-story cache version so old fallback stories are regenerated after provider-search fixes

### Phase 16 — NewsAPI Recheck & GNews Rate Limit Fix (done — Apr 2026)
- Re-checked activated NewsAPI.org key through `everything` and `top-headlines` endpoints using `X-Api-Key`; provider still returns `401 apiKeyInvalid`
- Fixed GNews query sanitizer order so dates are removed before score dash normalization, preventing syntax-error 400 responses
- Added global async GNews throttle across requests: at least 1.6 seconds between GNews calls
- Limited GNews to the first 2 strongest queries per match to respect free-tier request limits
- Added `refresh=true` query param for `/api/matches/{match_id}/story` so provider retries can be forced without changing frontend UI

### Phase 17 — Reliable RSS Match Report Sources (done — Apr 2026)
- Added RSS source layer before generic news APIs for match-specific stories
- Configured RSS feeds through backend env `MATCH_REPORT_RSS_FEEDS` instead of hardcoding URLs in frontend/code
- Initial reliable RSS feeds: BBC Sport Football and ESPN Soccer
- RSS items are normalized into the same article format as API providers: title, description, url, imageUrl, sourceName, publishedAt, provider
- RSS candidates use the same match relevance scoring and are preferred slightly when relevant
- Self-test: both RSS feeds return 200 and contain feed items; current sample football-data.org matches still had no exact RSS match-report source, so fallback remained correct

### Phase 18 — Official Premier League Match Reports Source (done — Apr 2026)
- Investigated official `premierleague.com` RSS/feed paths; no public RSS/XML feed found for match reports
- Found official Premier League content endpoint behind the Match Reports grid: `api.premierleague.com/content/premierleague/playlist/EN/4406257`
- Added backend env `MATCH_REPORT_CONTENT_SOURCES` for official JSON/content sources, separate from RSS feeds
- Added parser for official Premier League match-report playlist items and normalized them into the same article format
- Official PL source is preferred in relevance scoring and supplies source links/images when a match is matched
- Added Premier League alias matching (`Man Utd`, `Spurs`, `Palace`, `Wolves`, etc.) so official article titles match football-data.org team names
- Self-test with recent PL matches: Man United–Brentford, Arsenal–Newcastle, Liverpool–Crystal Palace all returned non-fallback stories with official source links/images

### Phase 19 — Automatic System Dark Mode (done — May 2026)
- Added system-driven dark mode via CSS `prefers-color-scheme: dark`; no in-app toggle required
- Dark palette covers app background, cards, navigation, modals, inputs, tables, story panels, and common badge states
- Added media-aware browser `theme-color` tags so supported mobile browsers can tint chrome for light/dark system modes
- Kept manifest splash background light to preserve existing PWA startup polish while the app itself adapts after load
- Verified with Playwright smoke tests: dark homepage, light homepage, and dark match modal load correctly

### Phase 20 — P0 Gamification: Daily Quiz & Achievements (done — May 2026)
- Added protected `/games` route and bottom navigation entry for a kid-friendly game hub
- Added backend gamification APIs: daily quiz, profile/scoreboard, answer submission, duplicate-answer protection
- Daily quiz uses football-data.org top scorers when available, with safe fallback quiz data if the scorer source is unavailable
- Added persistent MongoDB quiz attempts with points, streaks, recent attempts, and achievements/badges
- Added EN/RU/PT UI translations for the Games section and navigation labels
- Added regression tests in `/app/backend/tests/test_gamification_api.py`; verified 4/4 passing plus frontend smoke test

### Phase 21 — Crest Quiz Expansion (done — May 2026)
- Added a second daily quiz mode on `/games`: “Guess the Crest” / «Угадай эмблему»
- Added backend endpoints `/api/gamification/crest-quiz` and `/api/gamification/crest-quiz/answer`
- Crest quiz uses football-data.org league standings/team crests when available, with safe fallback club data if standings are unavailable
- The public crest quiz response hides `correctOptionId`; correctness is revealed only after authenticated answer submission
- Scoreboard/profile now aggregates attempts across player quiz and crest quiz
- Added EN/RU/PT labels for the crest quiz and updated regression coverage; verified 7/7 gamification tests passing

### Phase 22 — Backend Modular Refactor & Auth Hardening (done — May 2026)
- Split monolithic backend `server.py` into focused config/database/schema, service, and router modules while preserving all `/api` routes
- Added `login_attempts` persistence and lockout after 5 failed login attempts to harden custom JWT auth
- Added `/app/auth_testing.md` and regression coverage in `/app/backend/tests/test_refactor_regression_api.py`
- Verified backend regression: refactor suite 8/8 passing excluding platform-level ingress CORS check; existing gamification + match-story suites 13/13 passing

### Phase 23 — Backend Refactor Stage 2: Domain Router & Story Module Split (done — May 2026)
- Split the football aggregate router into focused domain routers: leagues, teams/players, matches, stories, and search
- Split match-story internals into utilities, external source fetchers, and child-friendly story builder; kept `match_story_service.py` as a compatibility facade
- Added regression coverage for `/api/search` and admin seed password repair (`test_auth_seed_admin.py`)
- Verified final backend regression: 24/24 tests passing locally against the running FastAPI backend; frontend smoke confirms Home → Leagues flow renders

### Phase 24 — Team “Did You Know?” Fun Facts (done — May 2026)
- Added a reusable `TeamFunFacts` component to team profile pages
- Shows 3 short child-friendly facts from existing team data: founded year, stadium, competition, coach, squad size, colors, with safe fallback facts when data is missing
- Added EN/RU/PT translations and data-testid coverage for the facts block
- Verified with frontend lint plus Playwright smoke tests on `/team/57` in English and Russian

### Phase 25 — Match Story UI Simplification (done — May 2026)
- Removed the visible “Why it matters” card from match-detail story sections
- Kept story title, summary, key points, images, source links, fallback badges, and optional highlight links intact
- Verified with frontend lint and Playwright smoke test opening the first homepage story modal; `match-story-why-card` is no longer rendered

### Phase 26 — Factual-Only Story Copy (done — May 2026)
- Reworked homepage story headlines to use factual scorelines instead of generic narrative phrases
- Reworked match-detail story summaries/key points to contain only score, teams, competition, half-time score, and sources
- Removed visible fallback explanatory note from story modals to save space
- Bumped match-story cache version to regenerate old cached narrative copy
- Verified with Python/JS lint, direct `/api/matches/{id}/story?refresh=true` check, Playwright story-modal smoke test, and match-story regression tests 6/6 passing

### Phase 27 — Admin Story Source Diagnostics (done — May 2026)
- Added protected admin route `/admin/stories` for viewing story-provider diagnostics per recent finished match
- Added backend admin APIs: `GET /api/admin/story-diagnostics` and `POST /api/admin/story-diagnostics/{match_id}/refresh`
- Story generation now stores provider diagnostics in MongoDB, including source status, HTTP status, query count, candidate articles, matched articles, and failure messages
- Diagnostics cover official PL content, RSS feeds, NewsAPI.org, NewsData.io, and GNews while keeping public `/api/matches/{match_id}/story` responses clean and factual-only
- Added admin-only homepage shortcut and EN/RU/PT translations for the diagnostics panel
- Verified with curl, Playwright smoke test, Python/JS lint, backend regression tests 21/21 passing, and testing-agent validation

## Key Technical Details
- Frontend: React, TailwindCSS, Shadcn UI, PWA Service Worker
- Backend: FastAPI, PyJWT (cookie auth), HTTPX, modular routers/services, split match-story provider/builder modules
- Database: MongoDB (caching + user favorites)
- API: football-data.org (free tier, 10 req/min, 5-30min cache)
- News providers: official PL content source, RSS feeds, GNews, NewsData.io, NewsAPI.org (backend-only config/keys, normalized article format, graceful fallback)

## DB Schema
- `users`: {email, hashed_password, favorites: {leagues: [], teams: []}}
- `football_cache`: {url, response_data, timestamp}
- `match_stories`: {matchId, language, title, summary, keyPoints, whyItMatters, isFallback, imageUrl, sources, videoUrl, generatedAt}
- `quiz_attempts`: {user_id, quizId, selectedOptionId, correctOptionId, isCorrect, pointsAwarded, answeredAt}
- `login_attempts`: {identifier, failed_count, last_failed_at, locked_until}

## Key API Endpoints
- `/api/auth/login`, `/api/auth/register`, `/api/auth/me`
- `/api/leagues`, `/api/leagues/{code}/standings`
- `/api/leagues/{code}/matches`, `/api/leagues/{code}/scorers`
- `/api/leagues/{code}/season` (new — season progress)
- `/api/matches/{match_id}` (with H2H)
- `/api/matches/{match_id}/story?lang=en|ru|pt` (cached child-friendly story for exact match)
- `/api/admin/story-diagnostics?lang=en|ru|pt&limit=10` (admin-only recent match story source diagnostics)
- `/api/admin/story-diagnostics/{match_id}/refresh?lang=en|ru|pt` (admin-only provider recheck + diagnostic cache update)
- `/api/teams/{team_id}`, `/api/players/{player_id}`
- `/api/search?q={query}`
- `/api/favorites`
- `/api/gamification/daily-quiz`, `/api/gamification/crest-quiz`, `/api/gamification/profile`

## Backlog

### P1 — Upcoming
- Push notifications for favorite team match alerts
- Optional language-switch UI automation for `Story of the Match`
- Expand gamification with match-score prediction and weekly challenge summaries

### P2 — Future
- Penalty stats in top scorers list
- Add more official league sources to story diagnostics/provider list

## Known Issues / Notes
- Route ordering in `routers/matches.py` is critical: `/matches/today` MUST precede `/matches/{match_id}`
- Homepage Match Stories headlines are generated programmatically; match-detail stories can use news providers or fallback to match data
- football-data.org free tier: 10 req/min limit, backend caches responses
- Match-specific stories use external news providers when a relevant article is found; fallback stories are generated from match data and saved in MongoDB
- Apr 2026 provider status: NewsData.io responds but often returns no exact report for current football-data.org matches; NewsAPI.org still rejects supplied key with 401 `apiKeyInvalid` even after activation recheck; GNews returns successfully with throttling but often no exact article for these matches. Fallback/cache flow remains essential.
- Apr 2026 RSS status: BBC Sport Football and ESPN Soccer feeds are reachable, but did not contain exact reports for tested sample matches.
- Apr 2026 Premier League status: official PL match-report content source works and provides exact sources/images for tested PL matches.
- May 2026 dark mode status: app now follows device/browser system theme automatically using `prefers-color-scheme`; there is intentionally no manual theme toggle yet.
- May 2026 gamification status: `/games` is live for logged-in users, daily quiz progress persists in MongoDB, and duplicate daily attempts do not award extra points.
- May 2026 crest quiz status: `/games` now includes both player and club-emblem daily quizzes; both persist to the same scoreboard/achievements profile.
- May 2026 backend refactor status: `server.py` is now a small assembly file; domain logic lives in services and routers. Auth lockout is active after 5 failed login attempts.
- May 2026 refactor stage 2 status: football routes and match-story logic are now split into smaller focused modules; `routers/football.py` remains as an aggregate compatibility router.
- May 2026 team fun facts status: team pages now include localized “Did you know?” facts using existing team profile data; no new external API dependency was added.
- May 2026 match story UI status: the “Why it matters” block is no longer shown in story modals; existing story API compatibility is preserved.
- May 2026 story copy status: story cards and modals now avoid generic narrative text and prioritize factual score/competition/source information.
- May 2026 admin diagnostics status: `/admin/stories` is available for admin users and shows provider-level success/failure per recent match; public story responses do not expose diagnostics.
- May 2026 CORS note: local FastAPI CORS returns explicit origin + credentials correctly; public preview OPTIONS preflight is intercepted by platform ingress and still returns wildcard CORS. Same-origin frontend flows continue to work, but cross-origin credentialed preflight requires ingress configuration outside app code.
- Response in Russian (user preference)
