from fastapi import APIRouter
from football_service import fetch_football_data

router = APIRouter(tags=["teams"])

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
