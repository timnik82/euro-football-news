# Goal Kick - European Football News PWA

## Problem Statement
Build a PWA for an 11-inch tablet for a 10-year-old kid with up-to-date news about European football matches including Premier League, Champions League, La Liga, Serie A, Bundesliga, Ligue 1, and Portuguese Primeira Liga.

## Architecture
- **Backend**: FastAPI (Python) with MongoDB caching
- **Frontend**: React PWA with Tailwind CSS + Shadcn UI
- **Data Source**: football-data.org v4 API (free tier)
- **Auth**: JWT cookie-based authentication
- **Database**: MongoDB for users, favorites, API cache

## User Personas
- Primary: 10-year-old football fan using 11-inch tablet
- Secondary: Parent setting up the account

## Core Requirements
- Live/recent match scores & results
- League standings tables
- Top scorers statistics
- Match stories/summaries (auto-generated)
- Simple login for saving favorites
- PWA installable on tablet

## What's Been Implemented (April 7, 2026)
- Full backend with auth, football API proxy with caching, favorites CRUD, story generator
- Homepage with upcoming matches, match stories, league cards
- League detail page with tabs (Table, Matches, Top Scorers)
- Login/Register page with stadium background
- Favorites page for saved teams/leagues
- Bottom navigation (Home, Leagues, Favorites, Profile)
- 7 leagues: PL, CL, PD, SA, BL1, FL1, PPL
- Kid-friendly "Vibrant Play" design with Fredoka/Nunito fonts
- PWA manifest configured
- **Service worker** with offline caching (network-first for API, cache-first for assets, stale-while-revalidate for team crests)
- Offline banner indicator when device is disconnected
- Apple PWA meta tags for iPad home screen install
- Auto-update mechanism when new service worker is deployed
- **Multi-language support** (English, Russian, Portuguese) with settings gear toggle
- Localized UI: navigation, page titles, match statuses, date formatting, story headlines
- Language preference persisted in localStorage

## Prioritized Backlog
### P0 (Done)
- Match scores, standings, scorers, stories ✅
- Auth system ✅
- Favorites system ✅
- Tablet-optimized UI ✅

### P1 (Next)
- Service worker for offline caching
- Push notifications for favorite team matches
- Match detail page with events timeline
- Team detail page

### P2 (Future)
- Dark mode toggle
- Multiple language support
- Share match stories
- Custom PWA icons
- Match day reminders
