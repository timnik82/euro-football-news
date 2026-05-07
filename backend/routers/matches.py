from datetime import datetime, timezone, timedelta
from fastapi import APIRouter
from config import COMPETITIONS
from football_service import fetch_football_data

router = APIRouter(tags=["matches"])

@router.get("/matches/today")
async def get_today_matches():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data = await fetch_football_data("/matches", cache_minutes=3, params={
        "dateFrom": today, "dateTo": today, "competitions": COMPETITIONS
    })
    return data.get("matches", [])

@router.get("/matches/upcoming")
async def get_upcoming_matches(days: int = 7):
    today = datetime.now(timezone.utc)
    date_from = today.strftime("%Y-%m-%d")
    date_to = (today + timedelta(days=min(days, 14))).strftime("%Y-%m-%d")
    data = await fetch_football_data("/matches", cache_minutes=10, params={
        "dateFrom": date_from, "dateTo": date_to, "competitions": COMPETITIONS
    })
    matches = [m for m in data.get("matches", []) if m.get("status") in ("SCHEDULED", "TIMED")]
    return matches[:30]

@router.get("/matches/recent")
async def get_recent_matches(days: int = 7):
    today = datetime.now(timezone.utc)
    date_from = (today - timedelta(days=min(days, 14))).strftime("%Y-%m-%d")
    date_to = today.strftime("%Y-%m-%d")
    data = await fetch_football_data("/matches", cache_minutes=5, params={
        "dateFrom": date_from, "dateTo": date_to, "competitions": COMPETITIONS
    })
    matches = [m for m in data.get("matches", []) if m.get("status") == "FINISHED"]
    matches.sort(key=lambda x: x.get("utcDate", ""), reverse=True)
    return matches[:30]

@router.get("/matches/{match_id}")
async def get_match_detail(match_id: int):
    match_data = await fetch_football_data(f"/matches/{match_id}", cache_minutes=5)
    h2h = None
    try:
        h2h = await fetch_football_data(f"/matches/{match_id}/head2head", cache_minutes=30, params={"limit": 5})
    except Exception:
        pass
    result = {
        "id": match_data.get("id"),
        "competition": match_data.get("competition"),
        "homeTeam": match_data.get("homeTeam"),
        "awayTeam": match_data.get("awayTeam"),
        "score": match_data.get("score"),
        "status": match_data.get("status"),
        "utcDate": match_data.get("utcDate"),
        "matchday": match_data.get("matchday"),
        "stage": match_data.get("stage"),
        "venue": match_data.get("venue"),
        "referees": match_data.get("referees", []),
        "season": match_data.get("season"),
    }
    if h2h:
        agg = h2h.get("aggregates", {})
        result["h2h"] = {
            "totalMatches": agg.get("numberOfMatches", 0),
            "totalGoals": agg.get("totalGoals", 0),
            "homeWins": agg.get("homeTeam", {}).get("wins", 0),
            "awayWins": agg.get("awayTeam", {}).get("wins", 0),
            "draws": agg.get("draws", 0),
            "recentMatches": [
                {
                    "homeTeam": m.get("homeTeam", {}).get("shortName", ""),
                    "awayTeam": m.get("awayTeam", {}).get("shortName", ""),
                    "homeScore": m.get("score", {}).get("fullTime", {}).get("home"),
                    "awayScore": m.get("score", {}).get("fullTime", {}).get("away"),
                    "date": m.get("utcDate", ""),
                    "homeCrest": m.get("homeTeam", {}).get("crest", ""),
                    "awayCrest": m.get("awayTeam", {}).get("crest", ""),
                }
                for m in h2h.get("matches", [])[:5]
            ],
        }
    return result
