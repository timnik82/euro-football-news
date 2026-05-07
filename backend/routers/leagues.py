from typing import Optional
from fastapi import APIRouter, HTTPException
from config import LEAGUE_COLORS, LEAGUES
from football_service import fetch_football_data

router = APIRouter(tags=["leagues"])

@router.get("/leagues")
async def get_leagues():
    leagues = []
    for code, info in LEAGUES.items():
        leagues.append({
            "code": code, "name": info["name"],
            "country": info["country"], "color": LEAGUE_COLORS.get(code, "#0EA5E9"),
            "emblem": info.get("emblem", "")
        })
    return leagues

@router.get("/leagues/{code}/season")
async def get_league_season(code: str):
    if code not in LEAGUES:
        raise HTTPException(404, "League not found")
    data = await fetch_football_data(f"/competitions/{code}", cache_minutes=30)
    cs = data.get("currentSeason") or {}
    total_matchdays = 38 if data.get("type") == "LEAGUE" else None
    return {
        "currentMatchday": cs.get("currentMatchday"),
        "totalMatchdays": total_matchdays,
        "startDate": cs.get("startDate"),
        "endDate": cs.get("endDate"),
        "winner": cs.get("winner"),
        "type": data.get("type"),
    }


@router.get("/leagues/{code}/matches")
async def get_league_matches(code: str, status: Optional[str] = None, limit: int = 20):
    if code not in LEAGUES:
        raise HTTPException(404, "League not found")
    params = {}
    if status:
        params["status"] = status
    data = await fetch_football_data(f"/competitions/{code}/matches", cache_minutes=5, params=params or None)
    matches = data.get("matches", [])
    if status == "FINISHED":
        matches.sort(key=lambda x: x.get("utcDate", ""), reverse=True)
    return matches[:limit]

@router.get("/leagues/{code}/standings")
async def get_league_standings(code: str):
    if code not in LEAGUES:
        raise HTTPException(404, "League not found")
    try:
        data = await fetch_football_data(f"/competitions/{code}/standings", cache_minutes=15)
        standings = data.get("standings", [])
        result = []
        for s in standings:
            if s.get("type") == "TOTAL":
                result.append({
                    "stage": s.get("stage", ""),
                    "group": s.get("group", ""),
                    "table": s.get("table", [])
                })
        return result if result else [{"stage": "", "group": "", "table": standings[0].get("table", [])}] if standings else []
    except HTTPException as e:
        if e.status_code in (403, 404):
            return []
        raise

@router.get("/leagues/{code}/scorers")
async def get_league_scorers(code: str, limit: int = 15):
    if code not in LEAGUES:
        raise HTTPException(404, "League not found")
    try:
        data = await fetch_football_data(f"/competitions/{code}/scorers", cache_minutes=30)
        return data.get("scorers", [])[:limit]
    except HTTPException as e:
        if e.status_code in (403, 404):
            return []
        raise
