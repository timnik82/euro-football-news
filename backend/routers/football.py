from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException
from config import COMPETITIONS, LEAGUE_COLORS, LEAGUES, MATCH_STORY_CACHE_VERSION
from database import db
from football_service import build_story_payload, fetch_football_data
from match_story_service import build_child_match_story, fetch_news_articles_for_match
from schemas import MatchStoryResponse

router = APIRouter(tags=["football"])

# Football endpoints
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


@router.get("/teams/{team_id}")
async def get_team(team_id: int):
    data = await fetch_football_data(f"/teams/{team_id}", cache_minutes=60)
    squad = data.get("squad", [])
    pos_map = {
        "Goalkeeper": "Goalkeeper",
        "Defence": "Defence", "Right-Back": "Defence", "Centre-Back": "Defence", "Left-Back": "Defence",
        "Midfield": "Midfield", "Defensive Midfield": "Midfield", "Central Midfield": "Midfield",
        "Attacking Midfield": "Midfield",
        "Offence": "Offence", "Right Winger": "Offence", "Left Winger": "Offence",
        "Centre-Forward": "Offence",
    }
    grouped = {"Goalkeeper": [], "Defence": [], "Midfield": [], "Offence": []}
    for p in squad:
        raw_pos = p.get("position") or "Unknown"
        group = pos_map.get(raw_pos, "Offence")
        grouped[group].append({
            "id": p.get("id"),
            "name": p.get("name"),
            "position": raw_pos,
            "nationality": p.get("nationality"),
            "dateOfBirth": p.get("dateOfBirth"),
        })
    coach = data.get("coach") or {}
    return {
        "id": data.get("id"),
        "name": data.get("name"),
        "shortName": data.get("shortName"),
        "crest": data.get("crest"),
        "venue": data.get("venue"),
        "address": data.get("address"),
        "website": data.get("website"),
        "founded": data.get("founded"),
        "clubColors": data.get("clubColors"),
        "coach": {
            "name": coach.get("name"),
            "nationality": coach.get("nationality"),
            "dateOfBirth": coach.get("dateOfBirth"),
            "contractUntil": coach.get("contract", {}).get("until"),
        } if coach.get("name") else None,
        "squad": grouped,
        "squadCount": len(squad),
        "runningCompetitions": [
            {"name": c.get("name"), "code": c.get("code"), "emblem": c.get("emblem")}
            for c in data.get("runningCompetitions", [])
        ],
    }

@router.get("/players/{player_id}")
async def get_player(player_id: int):
    data = await fetch_football_data(f"/persons/{player_id}", cache_minutes=60)
    ct = data.get("currentTeam") or {}
    contract = ct.get("contract") or {}
    return {
        "id": data.get("id"),
        "name": data.get("name"),
        "firstName": data.get("firstName"),
        "lastName": data.get("lastName"),
        "dateOfBirth": data.get("dateOfBirth"),
        "nationality": data.get("nationality"),
        "position": data.get("position"),
        "section": data.get("section"),
        "shirtNumber": data.get("shirtNumber"),
        "currentTeam": {
            "id": ct.get("id"),
            "name": ct.get("name"),
            "crest": ct.get("crest"),
        } if ct.get("name") else None,
        "contract": {
            "start": contract.get("start"),
            "until": contract.get("until"),
        } if contract.get("start") else None,
    }

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

@router.get("/matches/{match_id}/story", response_model=MatchStoryResponse)
async def get_match_story(match_id: int, lang: str = "en", refresh: bool = False):
    language = lang if lang in {"en", "ru", "pt"} else "en"
    cached_story = await db.match_stories.find_one(
        {"matchId": match_id, "language": language},
        {"_id": 0}
    )
    if not refresh and cached_story and cached_story.get("cacheVersion") == MATCH_STORY_CACHE_VERSION:
        return cached_story

    match_data = await fetch_football_data(f"/matches/{match_id}", cache_minutes=10)
    articles = []
    if match_data.get("status") == "FINISHED":
        articles = await fetch_news_articles_for_match(match_data, language)
    story_body = build_child_match_story(match_data, language, articles)
    story_doc = {
        "matchId": match_id,
        "language": language,
        "title": story_body["title"],
        "summary": story_body["summary"],
        "keyPoints": story_body["keyPoints"],
        "whyItMatters": story_body["whyItMatters"],
        "isFallback": story_body["isFallback"],
        "imageUrl": story_body.get("imageUrl"),
        "sources": story_body.get("sources", []),
        "videoUrl": story_body.get("videoUrl"),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "cacheVersion": MATCH_STORY_CACHE_VERSION,
    }
    await db.match_stories.update_one(
        {"matchId": match_id, "language": language},
        {"$set": story_doc},
        upsert=True
    )
    return story_doc


@router.get("/search")
async def search_teams_and_players(q: str = ""):
    if not q or len(q) < 2:
        return {"teams": [], "players": []}
    query = q.lower().strip()
    teams = []
    players = []
    seen_team_ids = set()
    seen_player_ids = set()

    for code, league_info in LEAGUES.items():
        # Teams from standings (served from cache)
        try:
            data = await fetch_football_data(f"/competitions/{code}/standings", cache_minutes=15)
            for s in data.get("standings", []):
                for row in s.get("table", []):
                    team = row.get("team", {})
                    tid = str(team.get("id", ""))
                    if tid and tid not in seen_team_ids:
                        name = team.get("name", "").lower()
                        short = team.get("shortName", "").lower()
                        if query in name or query in short:
                            seen_team_ids.add(tid)
                            teams.append({
                                "id": team["id"],
                                "name": team.get("name"),
                                "shortName": team.get("shortName"),
                                "crest": team.get("crest"),
                                "league": league_info["name"],
                                "leagueCode": code,
                            })
        except Exception:
            pass

        # Players from scorers (served from cache)
        try:
            data = await fetch_football_data(f"/competitions/{code}/scorers", cache_minutes=30)
            for scorer in data.get("scorers", []):
                player = scorer.get("player", {})
                pid = str(player.get("id", ""))
                if pid and pid not in seen_player_ids:
                    if query in player.get("name", "").lower():
                        seen_player_ids.add(pid)
                        t = scorer.get("team", {})
                        players.append({
                            "id": player["id"],
                            "name": player.get("name"),
                            "nationality": player.get("nationality"),
                            "team": t.get("shortName") or t.get("name"),
                            "teamCrest": t.get("crest"),
                            "goals": scorer.get("goals", 0),
                            "league": league_info["name"],
                            "leagueCode": code,
                        })
        except Exception:
            pass

    return {"teams": teams[:15], "players": players[:15]}


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

@router.get("/stories")
async def get_stories():
    today = datetime.now(timezone.utc)
    date_from = (today - timedelta(days=5)).strftime("%Y-%m-%d")
    date_to = today.strftime("%Y-%m-%d")
    try:
        data = await fetch_football_data("/matches", cache_minutes=10, params={
            "dateFrom": date_from, "dateTo": date_to,
            "status": "FINISHED", "competitions": COMPETITIONS
        })
    except Exception:
        return []
    stories = []
    for match in data.get("matches", []):
        story = build_story_payload(match)
        if story:
            stories.append(story)
    stories.sort(key=lambda x: x.get("date", ""), reverse=True)
    return stories[:20]
