import json
import httpx
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from config import FOOTBALL_API_BASE, FOOTBALL_API_KEY, logger
from database import db


async def fetch_football_data(endpoint, cache_minutes=5, params=None):
    cache_key = f"football:{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
    cached = await db.api_cache.find_one(
        {"key": cache_key, "expires_at": {"$gt": datetime.now(timezone.utc)}},
        {"_id": 0},
    )
    if cached:
        return cached["data"]

    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    try:
        async with httpx.AsyncClient() as http:
            resp = await http.get(f"{FOOTBALL_API_BASE}{endpoint}", headers=headers, params=params, timeout=15.0)
            if resp.status_code == 429:
                stale = await db.api_cache.find_one({"key": cache_key}, {"_id": 0})
                if stale:
                    return stale["data"]
                raise HTTPException(429, "Too many requests. Please wait a moment!")
            if resp.status_code != 200:
                logger.error(f"Football API {resp.status_code}: {resp.text[:300]}")
                stale = await db.api_cache.find_one({"key": cache_key}, {"_id": 0})
                if stale:
                    return stale["data"]
                raise HTTPException(502, "Could not fetch football data")
            data = resp.json()
    except httpx.RequestError as e:
        logger.error(f"Football API request error: {e}")
        stale = await db.api_cache.find_one({"key": cache_key}, {"_id": 0})
        if stale:
            return stale["data"]
        raise HTTPException(502, "Football data service unavailable")

    await db.api_cache.update_one(
        {"key": cache_key},
        {"$set": {"data": data, "expires_at": datetime.now(timezone.utc) + timedelta(minutes=cache_minutes), "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return data


def build_story_payload(match):
    home = match.get("homeTeam", {})
    away = match.get("awayTeam", {})
    ft = match.get("score", {}).get("fullTime", {})
    home_score = ft.get("home")
    away_score = ft.get("away")
    if home_score is None or away_score is None:
        return None
    comp = match.get("competition", {})
    return {
        "match_id": match.get("id"),
        "home_team": {"name": home.get("shortName") or home.get("name", "Home"), "crest": home.get("crest", "")},
        "away_team": {"name": away.get("shortName") or away.get("name", "Away"), "crest": away.get("crest", "")},
        "score": {"home": home_score, "away": away_score},
        "competition": {"name": comp.get("name", ""), "code": comp.get("code", ""), "emblem": comp.get("emblem", "")},
        "date": match.get("utcDate", ""),
        "matchday": match.get("matchday"),
    }