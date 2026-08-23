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
import uuid
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
GOOGLE_SESSION_DATA_URL = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
SESSION_MAX_AGE_SECONDS = 7 * 24 * 60 * 60

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

def build_public_user(user_doc):
    auth_provider = "password"
    if user_doc.get("google_account_id") and user_doc.get("password_hash"):
        auth_provider = "email_google"
    elif user_doc.get("google_account_id"):
        auth_provider = "google"

    return {
        "user_id": user_doc.get("user_id", ""),
        "name": user_doc.get("name", ""),
        "email": user_doc.get("email", ""),
        "role": user_doc.get("role", "user"),
        "picture": user_doc.get("picture", ""),
        "auth_provider": auth_provider,
    }

async def ensure_user_id(user_doc):
    if user_doc.get("user_id"):
        return user_doc
    generated_user_id = f"user_{uuid.uuid4().hex[:12]}"
    await db.users.update_one({"_id": user_doc["_id"]}, {"$set": {"user_id": generated_user_id}})
    user_doc["user_id"] = generated_user_id
    return user_doc

def normalize_expires_at(expires_at):
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at

async def get_user_from_session_token(session_token: str):
    session_doc = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session_doc:
        return None

    expires_at = normalize_expires_at(session_doc["expires_at"])
    if expires_at < datetime.now(timezone.utc):
        await db.user_sessions.delete_one({"session_token": session_token})
        raise HTTPException(401, "Session expired")

    user_doc = await db.users.find_one({"user_id": session_doc["user_id"]})
    if not user_doc:
        await db.user_sessions.delete_one({"session_token": session_token})
        raise HTTPException(401, "User not found")

    return await ensure_user_id(user_doc)

async def get_user_from_jwt(token: str):
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(401, "Invalid token type")
        user_doc = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user_doc:
            raise HTTPException(401, "User not found")
        user_doc = await ensure_user_id(user_doc)
        user_doc["_id"] = str(user_doc["_id"])
        return user_doc
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

async def get_current_user_doc(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token:
        user_doc = await get_user_from_session_token(session_token)
        if user_doc:
            user_doc["_id"] = str(user_doc["_id"])
            return user_doc

    token = request.cookies.get("access_token")
    auth = request.headers.get("Authorization", "")
    if not token and auth.startswith("Bearer "):
        token = auth[7:]
    if not token:
        raise HTTPException(401, "Not authenticated")

    user_doc = await get_user_from_session_token(token)
    if user_doc:
        user_doc["_id"] = str(user_doc["_id"])
        return user_doc
    return await get_user_from_jwt(token)

async def get_current_user(request: Request):
    user_doc = await get_current_user_doc(request)
    return build_public_user(user_doc)

def set_auth_cookies(response: Response, user_id: str, email: str):
    access = create_access_token(user_id, email)
    refresh = create_refresh_token(user_id)
    response.set_cookie("access_token", access, httponly=True, secure=False, samesite="lax", max_age=3600, path="/")
    response.set_cookie("refresh_token", refresh, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")

def set_google_session_cookie(response: Response, session_token: str):
    response.set_cookie(
        "session_token",
        session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=SESSION_MAX_AGE_SECONDS,
        path="/",
    )

def clear_auth_cookies(response: Response):
    response.delete_cookie("session_token", path="/", samesite="none")
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")

class RegisterInput(BaseModel):
    name: str
    email: str
    password: str

class LoginInput(BaseModel):
    email: str
    password: str

class GoogleSessionInput(BaseModel):
    session_id: str

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
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    user_doc = {
        "user_id": user_id,
        "name": data.name.strip(),
        "email": email,
        "password_hash": hashed,
        "role": "user",
        "picture": "",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = await db.users.insert_one(user_doc)
    internal_user_id = str(result.inserted_id)
    user_doc["_id"] = internal_user_id
    set_auth_cookies(response, internal_user_id, email)
    return build_public_user(user_doc)

@api_router.post("/auth/login")
async def login(data: LoginInput, response: Response):
    email = data.email.lower().strip()
    user = await db.users.find_one({"email": email})
    if not user or not user.get("password_hash") or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    user = await ensure_user_id(user)
    user_id = str(user["_id"])
    set_auth_cookies(response, user_id, email)
    return build_public_user(user)

async def fetch_google_session_data(session_id: str):
    try:
        async with httpx.AsyncClient() as http:
            response = await http.get(
                GOOGLE_SESSION_DATA_URL,
                headers={"X-Session-ID": session_id},
                timeout=15.0,
            )
    except httpx.RequestError as exc:
        logger.error(f"Google auth session request failed: {exc}")
        raise HTTPException(502, "Could not verify Google sign-in")

    if response.status_code != 200:
        logger.error(f"Google auth session error {response.status_code}: {response.text[:300]}")
        if response.status_code in (400, 401, 404):
            raise HTTPException(401, "Google sign-in session is invalid or expired")
        raise HTTPException(502, "Could not verify Google sign-in")

    return response.json()

@api_router.post("/auth/google/session")
async def exchange_google_session(data: GoogleSessionInput, response: Response):
    google_data = await fetch_google_session_data(data.session_id.strip())
    email = (google_data.get("email") or "").lower().strip()
    if not email:
        raise HTTPException(400, "Google sign-in did not return an email")

    existing_user = await db.users.find_one({"email": email})
    update_fields = {
        "picture": google_data.get("picture", ""),
        "google_account_id": google_data.get("id", ""),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if google_data.get("name"):
        update_fields["name"] = google_data["name"]

    if existing_user:
        existing_user = await ensure_user_id(existing_user)
        clean_updates = {key: value for key, value in update_fields.items() if value}
        if clean_updates:
            await db.users.update_one({"_id": existing_user["_id"]}, {"$set": clean_updates})
            existing_user.update(clean_updates)
        user_doc = existing_user
    else:
        user_doc = {
            "user_id": f"user_{uuid.uuid4().hex[:12]}",
            "name": google_data.get("name") or email.split("@")[0],
            "email": email,
            "role": "user",
            "picture": google_data.get("picture", ""),
            "google_account_id": google_data.get("id", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        result = await db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id

    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    await db.user_sessions.update_one(
        {"session_token": google_data["session_token"]},
        {
            "$set": {
                "user_id": user_doc["user_id"],
                "session_token": google_data["session_token"],
                "provider": "google",
                "expires_at": expires_at,
                "created_at": datetime.now(timezone.utc),
                "email": email,
            }
        },
        upsert=True,
    )
    clear_auth_cookies(response)
    set_google_session_cookie(response, google_data["session_token"])
    return build_public_user(user_doc)

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    clear_auth_cookies(response)
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
        user = await ensure_user_id(user)
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

@api_router.get("/matches/{match_id}")
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


@api_router.get("/search")
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


@api_router.get("/leagues/{code}/season")
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
    user = await get_current_user_doc(request)
    favs = await db.favorites.find({"user_id": user["_id"]}, {"_id": 0}).to_list(100)
    return favs

@api_router.post("/favorites")
async def toggle_favorite(data: FavoriteInput, request: Request):
    user = await get_current_user_doc(request)
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
            "user_id": f"user_{uuid.uuid4().hex[:12]}",
            "email": admin_email, "password_hash": hashed,
            "name": "Admin", "role": "admin",
            "picture": "",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info(f"Admin seeded: {admin_email}")
        return

    update_fields = {}
    if not existing.get("user_id"):
        update_fields["user_id"] = f"user_{uuid.uuid4().hex[:12]}"
    if not existing.get("picture"):
        update_fields["picture"] = ""
    if not verify_password(admin_password, existing["password_hash"]):
        update_fields["password_hash"] = hash_password(admin_password)
    if update_fields:
        await db.users.update_one({"email": admin_email}, {"$set": update_fields})

@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.users.create_index("user_id", unique=True, sparse=True)
    await db.api_cache.create_index("key", unique=True)
    await db.api_cache.create_index("expires_at", expireAfterSeconds=0)
    await db.favorites.create_index([("user_id", 1), ("type", 1), ("item_id", 1)], unique=True)
    await db.user_sessions.create_index("session_token", unique=True)
    await db.user_sessions.create_index("user_id")
    await db.user_sessions.create_index("expires_at", expireAfterSeconds=0)
    await seed_admin()
    os.makedirs("/app/memory", exist_ok=True)
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write(f"# Test Credentials\n\n## Admin\n- Email: {admin_email}\n- Password: {admin_password}\n- Role: admin\n\n")
        f.write("## Google OAuth\n- Provider: Emergent-managed Google social login\n- Google sign-in is available on both login and registration states\n- Existing app users are linked automatically when the Google email matches the same email\n- Allowed Google test accounts: use an approved Google account during manual QA (no app-managed password)\n\n")
        f.write("## Auth Endpoints\n- POST /api/auth/register\n- POST /api/auth/login\n- POST /api/auth/google/session\n- POST /api/auth/logout\n- GET /api/auth/me\n- POST /api/auth/refresh\n")

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
