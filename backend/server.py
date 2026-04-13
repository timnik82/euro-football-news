from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import bcrypt
import jwt
import httpx
import json
import secrets
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB
mongo_url = os.environ['MONGO_URL']
mongo_client = AsyncIOMotorClient(mongo_url)
db = mongo_client[os.environ['DB_NAME']]

# Football API
FOOTBALL_API_KEY = os.environ.get('FOOTBALL_API_KEY', '')
FOOTBALL_API_BASE = "https://api.football-data.org/v4"
COMPETITIONS = "PL,CL,PD,SA,BL1,FL1,PPL"

LEAGUES = {
    "PL": {"name": "Premier League", "country": "England", "emblem": "https://crests.football-data.org/PL.png"},
    "CL": {"name": "Champions League", "country": "Europe", "emblem": "https://crests.football-data.org/CL.png"},
    "PD": {"name": "La Liga", "country": "Spain", "emblem": "https://crests.football-data.org/laliga.png"},
    "SA": {"name": "Serie A", "country": "Italy", "emblem": "https://crests.football-data.org/c111.png"},
    "BL1": {"name": "Bundesliga", "country": "Germany", "emblem": "https://crests.football-data.org/BL1.png"},
    "FL1": {"name": "Ligue 1", "country": "France", "emblem": "https://crests.football-data.org/FL1.png"},
    "PPL": {"name": "Primeira Liga", "country": "Portugal", "emblem": "https://crests.football-data.org/PPL.png"},
}

LEAGUE_COLORS = {
    "PL": "#7C3AED",
    "CL": "#1E3A5F",
    "PD": "#F97316",
    "SA": "#059669",
    "BL1": "#DC2626",
    "FL1": "#1D4ED8",
    "PPL": "#15803D",
}

app = FastAPI()
api_router = APIRouter(prefix="/api")

# ============ AUTH ============
JWT_ALGORITHM = "HS256"

def get_jwt_secret():
    return os.environ["JWT_SECRET"]

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_access_token(user_id: str, email: str) -> str:
    payload = {"sub": user_id, "email": email, "exp": datetime.now(timezone.utc) + timedelta(hours=1), "type": "access"}
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "refresh"}
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        raise HTTPException(401, "Not authenticated")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(401, "Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(401, "User not found")
        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

def set_auth_cookies(response: Response, user_id: str, email: str):
    access = create_access_token(user_id, email)
    refresh = create_refresh_token(user_id)
    response.set_cookie("access_token", access, httponly=True, secure=False, samesite="lax", max_age=3600, path="/")
    response.set_cookie("refresh_token", refresh, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")

class RegisterInput(BaseModel):
    name: str
    email: str
    password: str

class LoginInput(BaseModel):
    email: str
    password: str

class FavoriteInput(BaseModel):
    type: str
    item_id: str
    name: str
    crest: str = ""
    league_code: str = ""

@api_router.post("/auth/register")
async def register(data: RegisterInput, response: Response):
    email = data.email.lower().strip()
    if await db.users.find_one({"email": email}):
        raise HTTPException(400, "Email already registered")
    hashed = hash_password(data.password)
    user_doc = {
        "name": data.name.strip(),
        "email": email,
        "password_hash": hashed,
        "role": "user",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    set_auth_cookies(response, user_id, email)
    return {"_id": user_id, "name": data.name.strip(), "email": email, "role": "user"}

@api_router.post("/auth/login")
async def login(data: LoginInput, response: Response):
    email = data.email.lower().strip()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    user_id = str(user["_id"])
    set_auth_cookies(response, user_id, email)
    return {"_id": user_id, "name": user["name"], "email": email, "role": user.get("role", "user")}

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out"}

@api_router.get("/auth/me")
async def get_me(request: Request):
    return await get_current_user(request)

@api_router.post("/auth/refresh")
async def refresh_token(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(401, "No refresh token")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(401, "User not found")
        user_id = str(user["_id"])
        access = create_access_token(user_id, user["email"])
        response.set_cookie("access_token", access, httponly=True, secure=False, samesite="lax", max_age=3600, path="/")
        return {"message": "Token refreshed"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid refresh token")

# ============ FOOTBALL API ============
async def fetch_football_data(endpoint, cache_minutes=5, params=None):
    cache_key = f"football:{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
    cached = await db.api_cache.find_one(
        {"key": cache_key, "expires_at": {"$gt": datetime.now(timezone.utc)}},
        {"_id": 0}
    )
    if cached:
        return cached["data"]

    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    try:
        async with httpx.AsyncClient() as http:
            resp = await http.get(
                f"{FOOTBALL_API_BASE}{endpoint}",
                headers=headers, params=params, timeout=15.0
            )
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
        upsert=True
    )
    return data

def generate_match_story(match):
    home = match.get("homeTeam", {})
    away = match.get("awayTeam", {})
    home_name = home.get("shortName") or home.get("name", "Home")
    away_name = away.get("shortName") or away.get("name", "Away")
    ft = match.get("score", {}).get("fullTime", {})
    home_score = ft.get("home")
    away_score = ft.get("away")
    if home_score is None or away_score is None:
        return None

    total = home_score + away_score
    diff = abs(home_score - away_score)

    if home_score > away_score:
        if diff >= 3:
            headline = f"{home_name} crushes {away_name} in dominant display!"
        elif diff == 1:
            headline = f"{home_name} edges past {away_name} in tight game!"
        else:
            headline = f"{home_name} wins comfortably against {away_name}!"
    elif away_score > home_score:
        if diff >= 3:
            headline = f"{away_name} demolishes {home_name} away from home!"
        elif diff == 1:
            headline = f"{away_name} sneaks a win at {home_name}!"
        else:
            headline = f"{away_name} triumphs at {home_name}!"
    else:
        if total == 0:
            headline = f"{home_name} and {away_name} play out goalless draw"
        else:
            headline = f"Exciting {home_score}-{away_score} draw between {home_name} and {away_name}!"

    if total >= 5:
        flavor = "A thrilling goal-fest that had fans on the edge of their seats!"
    elif total >= 3:
        flavor = "An entertaining match with plenty of action!"
    elif total == 0:
        flavor = "A defensive masterclass from both sides."
    else:
        flavor = "A competitive battle on the pitch!"

    comp = match.get("competition", {})
    return {
        "match_id": match.get("id"),
        "headline": headline,
        "summary": f"The final score was {home_score}-{away_score}. {flavor}",
        "home_team": {"name": home_name, "crest": home.get("crest", "")},
        "away_team": {"name": away_name, "crest": away.get("crest", "")},
        "score": {"home": home_score, "away": away_score},
        "competition": {"name": comp.get("name", ""), "code": comp.get("code", ""), "emblem": comp.get("emblem", "")},
        "date": match.get("utcDate", ""),
        "matchday": match.get("matchday"),
    }

# Football endpoints
@api_router.get("/leagues")
async def get_leagues():
    leagues = []
    for code, info in LEAGUES.items():
        leagues.append({
            "code": code, "name": info["name"],
            "country": info["country"], "color": LEAGUE_COLORS.get(code, "#0EA5E9"),
            "emblem": info.get("emblem", "")
        })
    return leagues


@api_router.get("/teams/{team_id}")
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

@api_router.get("/matches/{match_id}")

@api_router.get("/players/{player_id}")
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

async def get_match_detail(match_id: int):
    match_data = await fetch_football_data(f"/matches/{match_id}", cache_minutes=5)
    # Fetch head2head
    h2h = None
    try:
        h2h = await fetch_football_data(f"/matches/{match_id}/head2head", cache_minutes=30, params={"limit": 5})
    except Exception:
        pass
    # Clean response
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
    }
    if h2h:
        agg = h2h.get("aggregates", {})
        result["h2h"] = {
            "totalMatches": agg.get("numberOfMatches", 0),
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


@api_router.get("/matches/today")
async def get_today_matches():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data = await fetch_football_data("/matches", cache_minutes=3, params={
        "dateFrom": today, "dateTo": today, "competitions": COMPETITIONS
    })
    return data.get("matches", [])

@api_router.get("/matches/upcoming")
async def get_upcoming_matches(days: int = 7):
    today = datetime.now(timezone.utc)
    date_from = today.strftime("%Y-%m-%d")
    date_to = (today + timedelta(days=min(days, 14))).strftime("%Y-%m-%d")
    data = await fetch_football_data("/matches", cache_minutes=10, params={
        "dateFrom": date_from, "dateTo": date_to, "competitions": COMPETITIONS
    })
    matches = [m for m in data.get("matches", []) if m.get("status") in ("SCHEDULED", "TIMED")]
    return matches[:30]

@api_router.get("/matches/recent")
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

@api_router.get("/leagues/{code}/matches")
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

@api_router.get("/leagues/{code}/standings")
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

@api_router.get("/leagues/{code}/scorers")
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

@api_router.get("/stories")
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
        story = generate_match_story(match)
        if story:
            stories.append(story)
    stories.sort(key=lambda x: x.get("date", ""), reverse=True)
    return stories[:20]

# ============ FAVORITES ============
@api_router.get("/favorites")
async def get_favorites(request: Request):
    user = await get_current_user(request)
    favs = await db.favorites.find({"user_id": user["_id"]}, {"_id": 0}).to_list(100)
    return favs

@api_router.post("/favorites")
async def toggle_favorite(data: FavoriteInput, request: Request):
    user = await get_current_user(request)
    existing = await db.favorites.find_one({
        "user_id": user["_id"], "type": data.type, "item_id": data.item_id
    })
    if existing:
        await db.favorites.delete_one({"_id": existing["_id"]})
        return {"action": "removed", "type": data.type, "item_id": data.item_id}
    fav_doc = {
        "user_id": user["_id"], "type": data.type, "item_id": data.item_id,
        "name": data.name, "crest": data.crest, "league_code": data.league_code,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.favorites.insert_one(fav_doc)
    return {"action": "added", "type": data.type, "item_id": data.item_id, "name": data.name}

# ============ STARTUP ============
async def seed_admin():
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    existing = await db.users.find_one({"email": admin_email})
    if existing is None:
        hashed = hash_password(admin_password)
        await db.users.insert_one({
            "email": admin_email, "password_hash": hashed,
            "name": "Admin", "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info(f"Admin seeded: {admin_email}")
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one(
            {"email": admin_email},
            {"$set": {"password_hash": hash_password(admin_password)}}
        )

@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.api_cache.create_index("key", unique=True)
    await db.api_cache.create_index("expires_at", expireAfterSeconds=0)
    await db.favorites.create_index([("user_id", 1), ("type", 1), ("item_id", 1)], unique=True)
    await seed_admin()
    os.makedirs("/app/memory", exist_ok=True)
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write(f"# Test Credentials\n\n## Admin\n- Email: {admin_email}\n- Password: {admin_password}\n- Role: admin\n\n")
        f.write("## Auth Endpoints\n- POST /api/auth/register\n- POST /api/auth/login\n- POST /api/auth/logout\n- GET /api/auth/me\n- POST /api/auth/refresh\n")

@app.on_event("shutdown")
async def shutdown():
    mongo_client.close()

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
