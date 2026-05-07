from fastapi import APIRouter
from config import LEAGUES
from football_service import fetch_football_data

router = APIRouter(tags=["search"])

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
