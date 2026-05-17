from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, HTTPException, Query, Request

from auth_service import get_current_user
from config import COMPETITIONS
from database import db
from football_service import fetch_football_data
from match_story_cache_service import build_and_cache_match_story, normalize_story_language

router = APIRouter(prefix="/admin", tags=["admin"])


async def require_admin(request: Request):
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(403, "Admin access required")
    return user


def match_label(match: dict) -> str:
    home = (match.get("homeTeam") or {}).get("shortName") or (match.get("homeTeam") or {}).get("name") or "Home"
    away = (match.get("awayTeam") or {}).get("shortName") or (match.get("awayTeam") or {}).get("name") or "Away"
    return f"{home} — {away}"


def build_story_diagnostic_row(match: dict, cached_story: dict | None, language: str) -> dict:
    score = (match.get("score") or {}).get("fullTime") or {}
    diagnostics = []
    if cached_story:
        diagnostics = cached_story.get("diagnostics") or []
        if not diagnostics:
            diagnostics = [{
                "provider": "cache",
                "sourceName": "Cached story",
                "status": "matched" if cached_story.get("sources") else "fallback",
                "message": "This story was generated before provider diagnostics were recorded",
                "queryCount": 0,
                "candidateCount": len(cached_story.get("sources") or []),
                "matchedCount": len(cached_story.get("sources") or []),
            }]
    return {
        "matchId": match.get("id"),
        "language": language,
        "label": match_label(match),
        "competition": (match.get("competition") or {}).get("name") or "",
        "competitionCode": (match.get("competition") or {}).get("code") or "",
        "utcDate": match.get("utcDate"),
        "status": match.get("status"),
        "homeTeam": match.get("homeTeam"),
        "awayTeam": match.get("awayTeam"),
        "score": {"home": score.get("home"), "away": score.get("away")},
        "storyStatus": "not_checked" if not cached_story else "fallback" if cached_story.get("isFallback") else "source_found",
        "generatedAt": cached_story.get("generatedAt") if cached_story else None,
        "sourceCount": len(cached_story.get("sources") or []) if cached_story else 0,
        "diagnostics": diagnostics,
    }


async def recent_finished_matches(limit: int) -> list[dict]:
    today = datetime.now(timezone.utc)
    data = await fetch_football_data("/matches", cache_minutes=10, params={
        "dateFrom": (today - timedelta(days=7)).strftime("%Y-%m-%d"),
        "dateTo": today.strftime("%Y-%m-%d"),
        "status": "FINISHED",
        "competitions": COMPETITIONS,
    })
    matches = data.get("matches", [])
    matches.sort(key=lambda item: item.get("utcDate", ""), reverse=True)
    return matches[:limit]


@router.get("/story-diagnostics")
async def get_story_diagnostics(request: Request, lang: str = "en", limit: int = Query(10, ge=1, le=20)):
    await require_admin(request)
    language = normalize_story_language(lang)
    matches = await recent_finished_matches(limit)
    match_ids = [match.get("id") for match in matches if match.get("id")]
    cached_cursor = db.match_stories.find(
        {"matchId": {"$in": match_ids}, "language": language},
        {"_id": 0},
    )
    cached_by_match = {doc["matchId"]: doc async for doc in cached_cursor}
    return {
        "language": language,
        "matches": [build_story_diagnostic_row(match, cached_by_match.get(match.get("id")), language) for match in matches],
    }


@router.post("/story-diagnostics/{match_id}/refresh")
async def refresh_story_diagnostics(match_id: int, request: Request, lang: str = "en"):
    await require_admin(request)
    language = normalize_story_language(lang)
    story_doc = await build_and_cache_match_story(match_id, language)
    match_data = await fetch_football_data(f"/matches/{match_id}", cache_minutes=10)
    return build_story_diagnostic_row(match_data, story_doc, language)