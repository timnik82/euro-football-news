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
import asyncio
import time
import hashlib
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from urllib.parse import quote_plus
import re
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

# MongoDB
mongo_url = os.environ['MONGO_URL']
mongo_client = AsyncIOMotorClient(mongo_url)
db = mongo_client[os.environ['DB_NAME']]

# Football API
FOOTBALL_API_KEY = os.environ.get('FOOTBALL_API_KEY', '')
FOOTBALL_API_BASE = "https://api.football-data.org/v4"
COMPETITIONS = "PL,CL,PD,SA,BL1,FL1,PPL"
MATCH_STORY_CACHE_VERSION = "match-story-official-content-v2"

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
GNEWS_RATE_LIMIT_LOCK = asyncio.Lock()
GNEWS_RATE_LIMIT_STATE = {"last_request_at": 0.0}

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

class NormalizedArticle(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    imageUrl: Optional[str] = None
    sourceName: Optional[str] = None
    publishedAt: Optional[str] = None
    videoUrl: Optional[str] = None
    provider: Optional[str] = None

class MatchStoryResponse(BaseModel):
    matchId: int
    language: str
    title: str
    summary: str
    keyPoints: list[str]
    whyItMatters: str
    isFallback: bool
    imageUrl: Optional[str] = None
    sources: list[NormalizedArticle] = Field(default_factory=list)
    videoUrl: Optional[str] = None
    generatedAt: str

class QuizOption(BaseModel):
    id: str
    label: str

class DailyQuizResponse(BaseModel):
    quizId: str
    date: str
    league: dict
    question: str
    hints: list[str]
    options: list[QuizOption]
    rewardPoints: int

class DailyCrestQuizResponse(BaseModel):
    quizId: str
    date: str
    league: dict
    question: str
    hints: list[str]
    crestUrl: str
    options: list[QuizOption]
    rewardPoints: int

class QuizAnswerInput(BaseModel):
    quizId: str
    selectedOptionId: str
    language: str = "en"

class BadgeResponse(BaseModel):
    id: str
    title: str
    description: str
    icon: str
    unlocked: bool

class QuizAnswerResponse(BaseModel):
    quizId: str
    selectedOptionId: str
    correctOptionId: str
    isCorrect: bool
    pointsAwarded: int
    alreadyAnswered: bool
    explanation: str
    profile: dict
    badges: list[BadgeResponse]

class GamificationProfileResponse(BaseModel):
    totalPoints: int
    quizzesPlayed: int
    correctAnswers: int
    currentStreak: int
    todayAnswered: bool
    recentAttempts: list[dict]
    badges: list[BadgeResponse]

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
        "home_team": {
            "name": home.get("shortName") or home.get("name", "Home"),
            "crest": home.get("crest", ""),
        },
        "away_team": {
            "name": away.get("shortName") or away.get("name", "Away"),
            "crest": away.get("crest", ""),
        },
        "score": {"home": home_score, "away": away_score},
        "competition": {"name": comp.get("name", ""), "code": comp.get("code", ""), "emblem": comp.get("emblem", "")},
        "date": match.get("utcDate", ""),
        "matchday": match.get("matchday"),
    }

def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())

def parse_article_date(value: str):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except Exception:
        try:
            parsed = parsedate_to_datetime(value)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except Exception:
            return None

def strip_html(value: str) -> str:
    return clean_text(re.sub(r"<[^>]+>", " ", value or ""))

def normalize_article_payload(provider: str, article: dict) -> Optional[dict]:
    if provider == "gnews":
        title = article.get("title")
        url = article.get("url")
        source_name = (article.get("source") or {}).get("name")
        image_url = article.get("image")
        published_at = article.get("publishedAt")
        description = article.get("description")
    elif provider == "newsdata":
        title = article.get("title")
        url = article.get("link")
        source_name = article.get("source_id") or article.get("source_name")
        image_url = article.get("image_url")
        published_at = article.get("pubDate")
        description = article.get("description")
    elif provider == "newsapi":
        title = article.get("title")
        url = article.get("url")
        source_name = (article.get("source") or {}).get("name")
        image_url = article.get("urlToImage")
        published_at = article.get("publishedAt")
        description = article.get("description")
    elif provider == "rss":
        title = article.get("title")
        url = article.get("url")
        source_name = article.get("sourceName")
        image_url = article.get("imageUrl")
        published_at = article.get("publishedAt")
        description = article.get("description")
    elif provider == "official_content":
        title = article.get("title")
        url = article.get("url")
        source_name = article.get("sourceName")
        image_url = article.get("imageUrl")
        published_at = article.get("publishedAt")
        description = article.get("description")
    else:
        return None

    title = clean_text(title)
    url = clean_text(url)
    if not title or not url:
        return None
    return {
        "title": title[:240],
        "description": clean_text(description)[:320] if description else None,
        "url": url,
        "imageUrl": image_url or None,
        "sourceName": clean_text(source_name) or provider,
        "publishedAt": published_at,
        "videoUrl": article.get("video_url") or article.get("videoUrl"),
        "provider": provider,
    }

def team_aliases(team: dict) -> list[str]:
    aliases = []
    for key in ("name", "shortName", "tla"):
        value = clean_text(team.get(key, ""))
        if value and value not in aliases:
            aliases.append(value)
    name = clean_text(team.get("name", ""))
    for suffix in (" FC", " CF", " AFC", " SAD"):
        if name.endswith(suffix):
            aliases.append(name[:-len(suffix)])
    alias_map = {
        "manchester united": ["Man Utd", "Manchester United"],
        "man united": ["Man Utd", "Manchester United"],
        "manchester city": ["Man City", "Manchester City"],
        "tottenham hotspur": ["Tottenham", "Spurs"],
        "crystal palace": ["Crystal Palace", "Palace"],
        "wolverhampton wanderers": ["Wolverhampton", "Wolves"],
        "nottingham forest": ["Nottingham Forest", "Forest"],
        "west ham united": ["West Ham", "West Ham United"],
        "newcastle united": ["Newcastle", "Newcastle United"],
        "brighton hove albion": ["Brighton", "Brighton & Hove Albion"],
        "aston villa": ["Aston Villa", "Villa"],
        "leeds united": ["Leeds", "Leeds United"],
    }
    team_text = " ".join(aliases).lower().replace("&", " ")
    for key, mapped_aliases in alias_map.items():
        if key in team_text:
            aliases.extend(mapped_aliases)
    return [a for a in aliases if len(a) >= 2]

def contains_any(text: str, aliases: list[str]) -> bool:
    text_low = text.lower()
    return any(alias.lower() in text_low for alias in aliases)

def article_relevance_score(article: dict, match: dict) -> int:
    text = f"{article.get('title', '')} {article.get('description', '')} {article.get('sourceName', '')}".lower()
    blocked_terms = [
        "transfer", "scout", "rumour", "rumor", "roster", "prediction", "predicted lineup",
        "lineup", "line-up", "betting", "odds", "signing", "contract", "market"
    ]
    if any(term in text for term in blocked_terms):
        return 0
    home = match.get("homeTeam") or {}
    away = match.get("awayTeam") or {}
    competition = match.get("competition") or {}
    score = match.get("score", {}).get("fullTime", {})
    home_score = score.get("home")
    away_score = score.get("away")
    score_value = 0
    has_home = contains_any(text, team_aliases(home))
    has_away = contains_any(text, team_aliases(away))
    has_competition = bool(competition.get("name") and competition["name"].lower() in text)
    has_score = False
    has_match_keyword = any(k in text for k in ["match report", "report", "highlights", "win", "draw", "beat", "defeat", "victory", "held", "equaliser", "goals"])

    if has_home:
        score_value += 5
    if has_away:
        score_value += 5
    if has_competition:
        score_value += 2
    if home_score is not None and away_score is not None:
        patterns = [f"{home_score}-{away_score}", f"{home_score}:{away_score}", f"{home_score} {away_score}"]
        if any(p in text for p in patterns):
            has_score = True
            score_value += 4
    if has_match_keyword:
        score_value += 2
    if article.get("imageUrl"):
        score_value += 1

    published = parse_article_date(article.get("publishedAt"))
    if published and match.get("utcDate"):
        match_date = parse_article_date(match.get("utcDate"))
        if match_date and abs((published - match_date).days) <= 5:
            score_value += 2

    source = (article.get("sourceName") or "").lower()
    trusted = ["uefa", "premier league", "bbc", "sky sports", "espn", "the athletic", "goal", "marca", "record", "abola", "bundesliga", "ligue 1", "serie a"]
    if any(name in source for name in trusted):
        score_value += 3
    if not (has_home and has_away):
        return 0
    if not (has_score or has_competition or has_match_keyword):
        return 0
    return score_value

def build_match_queries(match: dict) -> list[str]:
    home_team = match.get("homeTeam") or {}
    away_team = match.get("awayTeam") or {}
    home = home_team.get("shortName") or home_team.get("name") or ""
    away = away_team.get("shortName") or away_team.get("name") or ""
    home_full = home_team.get("name") or home
    away_full = away_team.get("name") or away
    competition = (match.get("competition") or {}).get("name") or ""
    score = match.get("score", {}).get("fullTime", {})
    home_score = score.get("home")
    away_score = score.get("away")
    date = (match.get("utcDate") or "")[:10]
    queries = []
    if home and away and home_score is not None and away_score is not None:
        queries.append(f"{home} {away} {home_score}-{away_score} {date} match report")
        queries.append(f"{home} {away} {home_score} {away_score} highlights")
    if home and away and competition:
        queries.append(f"{home} vs {away} {competition} match report")
    if home_full != home or away_full != away:
        queries.append(f"{home_full} {away_full} football match report")
    if home and away:
        queries.append(f"{home} {away} highlights")
        if home_score is not None and away_score is not None:
            if home_score == away_score:
                queries.append(f"{home} {away} draw")
            else:
                winner = home if home_score > away_score else away
                loser = away if home_score > away_score else home
                queries.append(f"{winner} win against {loser}")
    deduped = []
    for query in queries:
        if query and query not in deduped:
            deduped.append(query)
    return deduped[:4]

def provider_safe_query(query: str, provider_name: str) -> str:
    if provider_name == "gnews":
        without_date = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "", query)
        without_score_dash = re.sub(r"\b(\d+)-(\d+)\b", r"\1 \2", without_date)
        return clean_text(without_score_dash)
    return clean_text(query)

async def wait_for_gnews_slot():
    async with GNEWS_RATE_LIMIT_LOCK:
        elapsed = time.monotonic() - GNEWS_RATE_LIMIT_STATE["last_request_at"]
        if elapsed < 1.6:
            await asyncio.sleep(1.6 - elapsed)
        GNEWS_RATE_LIMIT_STATE["last_request_at"] = time.monotonic()

def configured_rss_feeds() -> list[dict]:
    raw_feeds = os.environ.get("MATCH_REPORT_RSS_FEEDS")
    if not raw_feeds:
        return []
    try:
        feeds = json.loads(raw_feeds)
        return [feed for feed in feeds if feed.get("name") and feed.get("url")]
    except Exception as e:
        logger.info(f"RSS feed config invalid: {e}")
        return []

def configured_content_sources() -> list[dict]:
    raw_sources = os.environ.get("MATCH_REPORT_CONTENT_SOURCES")
    if not raw_sources:
        return []
    try:
        sources = json.loads(raw_sources)
        return [source for source in sources if source.get("name") and source.get("url")]
    except Exception as e:
        logger.info(f"Content source config invalid: {e}")
        return []

def rss_child_text(item, tag_name: str) -> str:
    node = item.find(tag_name)
    return node.text if node is not None and node.text else ""

def rss_item_image(item) -> Optional[str]:
    enclosure = item.find("enclosure")
    if enclosure is not None:
        enclosure_type = enclosure.attrib.get("type", "")
        enclosure_url = enclosure.attrib.get("url")
        if enclosure_url and enclosure_type.startswith("image"):
            return enclosure_url
    for child in list(item):
        tag = child.tag.lower()
        if tag.endswith("thumbnail") or tag.endswith("content"):
            url = child.attrib.get("url")
            medium = child.attrib.get("medium", "")
            content_type = child.attrib.get("type", "")
            if url and ("image" in content_type or medium == "image" or tag.endswith("thumbnail")):
                return url
    return None

def parse_rss_articles(xml_text: str, feed_name: str) -> list[dict]:
    try:
        root = ET.fromstring(xml_text)
    except Exception as e:
        logger.info(f"RSS parse failed for {feed_name}: {e}")
        return []
    articles = []
    for item in root.findall(".//item")[:25]:
        title = rss_child_text(item, "title")
        url = rss_child_text(item, "link")
        description = strip_html(rss_child_text(item, "description"))
        published_at = rss_child_text(item, "pubDate") or rss_child_text(item, "date")
        normalized = normalize_article_payload("rss", {
            "title": title,
            "url": url,
            "description": description,
            "publishedAt": parse_article_date(published_at).isoformat() if parse_article_date(published_at) else published_at,
            "imageUrl": rss_item_image(item),
            "sourceName": feed_name,
        })
        if normalized:
            articles.append(normalized)
    return articles

async def fetch_rss_articles_for_match(match: dict) -> list[dict]:
    feeds = configured_rss_feeds()
    if not feeds:
        return []
    articles = []
    seen_urls = set()
    async with httpx.AsyncClient(timeout=10.0, headers={"User-Agent": "GoalKickKidApp/1.0"}) as http:
        for feed in feeds:
            try:
                resp = await http.get(feed["url"])
                if resp.status_code != 200:
                    logger.info(f"RSS feed {feed['name']} returned {resp.status_code}")
                    continue
                for article in parse_rss_articles(resp.text, feed["name"]):
                    if article["url"] in seen_urls:
                        continue
                    relevance = article_relevance_score(article, match)
                    if relevance >= 9:
                        article["relevanceScore"] = relevance + 2
                        articles.append(article)
                        seen_urls.add(article["url"])
            except Exception as e:
                logger.info(f"RSS feed {feed['name']} failed: {e}")
    articles.sort(key=lambda a: (a.get("relevanceScore", 0), 1 if a.get("imageUrl") else 0, a.get("publishedAt") or ""), reverse=True)
    for article in articles:
        article.pop("relevanceScore", None)
    return articles[:5]

def official_content_article_url(item: dict) -> str:
    match_ref = next(
        (ref for ref in item.get("references", []) if ref.get("type") == "SDP_FOOTBALL_MATCH" and ref.get("sid")),
        None,
    )
    if match_ref:
        return f"https://www.premierleague.com/en/match/{match_ref['sid']}/overview"
    article_id = item.get("id")
    segment = item.get("titleUrlSegment")
    if article_id and segment:
        return f"https://www.premierleague.com/en/news/{article_id}/{segment}"
    return item.get("hotlinkUrl") or "https://www.premierleague.com/en/news"

def parse_official_content_articles(payload: dict, source_name: str) -> list[dict]:
    raw_items = payload.get("items", [])
    articles = []
    for raw_item in raw_items[:20]:
        item = raw_item.get("response") or raw_item
        title = item.get("title")
        url = official_content_article_url(item)
        description = item.get("description") or item.get("summary") or item.get("contentSummary")
        normalized = normalize_article_payload("official_content", {
            "title": title,
            "url": url,
            "description": description,
            "publishedAt": item.get("date"),
            "imageUrl": item.get("imageUrl"),
            "sourceName": source_name,
        })
        if normalized:
            articles.append(normalized)
    return articles

async def fetch_official_content_articles_for_match(match: dict) -> list[dict]:
    sources = configured_content_sources()
    if not sources:
        return []
    articles = []
    seen_urls = set()
    async with httpx.AsyncClient(timeout=10.0, headers={
        "User-Agent": "GoalKickKidApp/1.0",
        "Accept": "application/json",
        "Origin": "https://www.premierleague.com",
        "Referer": "https://www.premierleague.com/en/news",
    }) as http:
        for source in sources:
            try:
                resp = await http.get(source["url"])
                if resp.status_code != 200:
                    logger.info(f"Official content source {source['name']} returned {resp.status_code}")
                    continue
                for article in parse_official_content_articles(resp.json(), source["name"]):
                    if article["url"] in seen_urls:
                        continue
                    relevance = article_relevance_score(article, match)
                    if relevance >= 9:
                        article["relevanceScore"] = relevance + 4
                        articles.append(article)
                        seen_urls.add(article["url"])
            except Exception as e:
                logger.info(f"Official content source {source['name']} failed: {e}")
    articles.sort(key=lambda a: (a.get("relevanceScore", 0), 1 if a.get("imageUrl") else 0, a.get("publishedAt") or ""), reverse=True)
    for article in articles:
        article.pop("relevanceScore", None)
    return articles[:5]

async def fetch_news_articles_for_match(match: dict, language: str) -> list[dict]:
    news_language = "en"
    newsapi_key = os.environ.get("NEWSAPI_KEY")
    provider_configs = [
        {
            "name": "newsapi",
            "url": "https://newsapi.org/v2/everything",
            "key": newsapi_key,
            "params": lambda q: {"q": q, "language": news_language, "pageSize": 10, "sortBy": "publishedAt"},
            "headers": lambda: {"X-Api-Key": newsapi_key} if newsapi_key else {},
            "extract": lambda payload: payload.get("articles", []),
        },
        {
            "name": "newsdata",
            "url": "https://newsdata.io/api/1/news",
            "key": os.environ.get("NEWSDATA_API_KEY"),
            "params": lambda q: {"q": q, "apikey": os.environ.get("NEWSDATA_API_KEY"), "language": news_language, "category": "sports", "size": 10},
            "headers": lambda: {},
            "extract": lambda payload: payload.get("results", []),
        },
        {
            "name": "gnews",
            "url": "https://gnews.io/api/v4/search",
            "key": os.environ.get("GNEWS_API_KEY"),
            "params": lambda q: {"q": q, "token": os.environ.get("GNEWS_API_KEY"), "lang": news_language, "max": 3},
            "headers": lambda: {},
            "extract": lambda payload: payload.get("articles", []),
        },
    ]
    queries = build_match_queries(match)
    articles = await fetch_official_content_articles_for_match(match)
    rss_articles = await fetch_rss_articles_for_match(match)
    articles.extend([article for article in rss_articles if article["url"] not in {item["url"] for item in articles}])
    seen_urls = {article["url"] for article in articles}

    async with httpx.AsyncClient(timeout=7.0) as http:
        for query_index, query in enumerate(queries):
            for provider in provider_configs:
                if not provider["key"]:
                    continue
                if provider["name"] == "gnews" and query_index >= 2:
                    continue
                try:
                    safe_query = provider_safe_query(query, provider["name"])
                    if provider["name"] == "gnews":
                        await wait_for_gnews_slot()
                    resp = await http.get(
                        provider["url"],
                        params=provider["params"](safe_query),
                        headers=provider["headers"](),
                    )
                    if resp.status_code != 200:
                        logger.info(f"News provider {provider['name']} returned {resp.status_code}")
                        continue
                    payload = resp.json()
                    for raw_article in provider["extract"](payload):
                        normalized = normalize_article_payload(provider["name"], raw_article)
                        if not normalized or normalized["url"] in seen_urls:
                            continue
                        relevance = article_relevance_score(normalized, match)
                        if relevance >= 9:
                            normalized["relevanceScore"] = relevance
                            articles.append(normalized)
                            seen_urls.add(normalized["url"])
                except Exception as e:
                    logger.info(f"News provider {provider['name']} failed: {e}")

    articles.sort(key=lambda a: (a.get("relevanceScore", 0), 1 if a.get("imageUrl") else 0, a.get("publishedAt") or ""), reverse=True)
    for article in articles:
        article.pop("relevanceScore", None)
    return articles[:5]

def build_child_match_story(match: dict, language: str, articles: list[dict]) -> dict:
    lang = language if language in {"en", "ru", "pt"} else "en"
    home = (match.get("homeTeam") or {}).get("shortName") or (match.get("homeTeam") or {}).get("name") or "Home"
    away = (match.get("awayTeam") or {}).get("shortName") or (match.get("awayTeam") or {}).get("name") or "Away"
    comp = (match.get("competition") or {}).get("name") or "football"
    score = match.get("score", {}).get("fullTime", {})
    half = match.get("score", {}).get("halfTime", {})
    h = score.get("home")
    a = score.get("away")
    match_date = (match.get("utcDate") or "")[:10]
    has_score = h is not None and a is not None
    winner = home if has_score and h > a else away if has_score and a > h else None
    is_draw = has_score and h == a
    source_names = [s.get("sourceName") for s in articles[:3] if s.get("sourceName")]
    source_phrase = ", ".join(source_names[:2])

    if lang == "ru":
        title = f"История матча: {home} — {away}"
        if has_score:
            if is_draw:
                summary = f"{home} и {away} сыграли {h}:{a} в турнире {comp}. Обе команды получили по одному очку, а матч стал хорошим примером того, как важно сохранять концентрацию до финального свистка."
            else:
                summary = f"{winner} победил в матче {home} — {away} со счётом {h}:{a} в турнире {comp}. Это была важная игра, где решали точность, терпение и командная работа."
        else:
            summary = f"Матч {home} — {away} проходит в турнире {comp}. Мы собрали короткую и понятную историю по доступным данным матча."
        key_points = [
            f"Игра: {home} против {away}.",
            f"Турнир: {comp}.",
        ]
        if has_score:
            key_points.append(f"Итоговый счёт: {h}:{a}.")
        if half.get("home") is not None and half.get("away") is not None:
            key_points.append(f"После первого тайма было {half.get('home')}:{half.get('away')}.")
        if articles:
            key_points.append(f"Мы нашли внешние источники по этому матчу: {source_phrase}.")
        why = "Этот результат важен, потому что каждая игра влияет на таблицу, уверенность команд и настроение болельщиков. По таким матчам удобно учиться читать счёт, замечать ход игры и понимать турнир."
        fallback_note = "Полный внешний обзор пока не найден, поэтому история составлена по данным матча."
    elif lang == "pt":
        title = f"História do jogo: {home} — {away}"
        if has_score:
            if is_draw:
                summary = f"{home} e {away} empataram {h}-{a} em {comp}. As duas equipas somaram um ponto, num jogo que mostra como a concentração conta até ao fim."
            else:
                summary = f"{winner} venceu o jogo {home} — {away} por {h}-{a} em {comp}. Foi uma partida em que precisão, paciência e trabalho de equipa fizeram diferença."
        else:
            summary = f"O jogo {home} — {away} faz parte de {comp}. Reunimos uma história curta e simples com os dados disponíveis."
        key_points = [
            f"Jogo: {home} contra {away}.",
            f"Competição: {comp}.",
        ]
        if has_score:
            key_points.append(f"Resultado final: {h}-{a}.")
        if half.get("home") is not None and half.get("away") is not None:
            key_points.append(f"Ao intervalo estava {half.get('home')}-{half.get('away')}.")
        if articles:
            key_points.append(f"Encontrámos fontes externas sobre este jogo: {source_phrase}.")
        why = "Este resultado importa porque cada jogo mexe com a tabela, a confiança das equipas e a energia dos adeptos. Também ajuda a aprender a ler resultados e a perceber uma competição."
        fallback_note = "Ainda não encontrámos uma reportagem completa, por isso a história usa os dados do jogo."
    else:
        title = f"Story of the Match: {home} — {away}"
        if has_score:
            if is_draw:
                summary = f"{home} and {away} finished {h}-{a} in {comp}. Both teams earned one point, and the match showed why focus matters until the final whistle."
            else:
                summary = f"{winner} won the match between {home} and {away} by {h}-{a} in {comp}. It was a game where accuracy, patience, and teamwork made the difference."
        else:
            summary = f"{home} and {away} meet in {comp}. Here is a short, simple story from the match information we have so far."
        key_points = [
            f"Match: {home} against {away}.",
            f"Competition: {comp}.",
        ]
        if has_score:
            key_points.append(f"Final score: {h}-{a}.")
        if half.get("home") is not None and half.get("away") is not None:
            key_points.append(f"At half-time it was {half.get('home')}-{half.get('away')}.")
        if articles:
            key_points.append(f"External match sources were found, including {source_phrase}.")
        why = "This result matters because every match can shape the table, team confidence, and supporter excitement. It is also a great way to learn how scores and competitions work."
        fallback_note = "We could not find a full story for this match yet, so this story uses the match result data."

    if not articles and fallback_note not in key_points:
        key_points.append(fallback_note)

    image_url = next((a.get("imageUrl") for a in articles if a.get("imageUrl")), None)
    video_url = next((a.get("videoUrl") for a in articles if a.get("videoUrl")), None)
    return {
        "title": title,
        "summary": summary,
        "keyPoints": key_points[:5],
        "whyItMatters": why,
        "isFallback": len(articles) == 0,
        "imageUrl": image_url,
        "sources": articles[:3],
        "videoUrl": video_url,
        "matchDate": match_date,
    }

# ============ GAMIFICATION ============
QUIZ_LEAGUE_CODES = ["PL", "PD", "SA", "BL1", "FL1", "PPL"]
QUIZ_REWARD_POINTS = 10
FALLBACK_QUIZ_PLAYERS = [
    {
        "player": {"id": 101, "name": "Erling Haaland", "nationality": "Norway"},
        "team": {"name": "Manchester City", "shortName": "Man City", "crest": "https://crests.football-data.org/65.png"},
        "goals": 18,
    },
    {
        "player": {"id": 102, "name": "Kylian Mbappé", "nationality": "France"},
        "team": {"name": "Real Madrid", "shortName": "Real Madrid", "crest": "https://crests.football-data.org/86.png"},
        "goals": 17,
    },
    {
        "player": {"id": 103, "name": "Harry Kane", "nationality": "England"},
        "team": {"name": "FC Bayern München", "shortName": "Bayern", "crest": "https://crests.football-data.org/5.png"},
        "goals": 19,
    },
    {
        "player": {"id": 104, "name": "Robert Lewandowski", "nationality": "Poland"},
        "team": {"name": "FC Barcelona", "shortName": "Barcelona", "crest": "https://crests.football-data.org/81.png"},
        "goals": 16,
    },
]
FALLBACK_QUIZ_TEAMS = [
    {"id": 65, "name": "Manchester City FC", "shortName": "Man City", "crest": "https://crests.football-data.org/65.png"},
    {"id": 86, "name": "Real Madrid CF", "shortName": "Real Madrid", "crest": "https://crests.football-data.org/86.png"},
    {"id": 5, "name": "FC Bayern München", "shortName": "Bayern", "crest": "https://crests.football-data.org/5.png"},
    {"id": 81, "name": "FC Barcelona", "shortName": "Barcelona", "crest": "https://crests.football-data.org/81.png"},
    {"id": 57, "name": "Arsenal FC", "shortName": "Arsenal", "crest": "https://crests.football-data.org/57.png"},
    {"id": 109, "name": "Juventus FC", "shortName": "Juventus", "crest": "https://crests.football-data.org/109.png"},
]

def stable_number(seed: str, modulo: int) -> int:
    if modulo <= 0:
        return 0
    return int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % modulo

def quiz_option_id(name: str) -> str:
    return "player-" + hashlib.sha1(name.encode("utf-8")).hexdigest()[:12]

def team_quiz_option_id(team: dict) -> str:
    raw_id = str(team.get("id") or team.get("name") or team.get("shortName") or "team")
    return "team-" + hashlib.sha1(raw_id.encode("utf-8")).hexdigest()[:12]

def localized_quiz_text(lang: str, key: str, values: dict) -> str:
    language = lang if lang in {"en", "ru", "pt"} else "en"
    templates = {
        "en": {
            "question": "Guess the player: who has scored {goals} goals for {team}?",
            "league": "League: {league}",
            "team": "Club: {team}",
            "nationality": "Nationality: {nationality}",
            "correct": "Correct! It is {player} from {team}. You earned {points} points.",
            "wrong": "Almost! The right answer is {player} from {team}. Try again tomorrow.",
        },
        "ru": {
            "question": "Угадай игрока: кто забил {goals} голов за {team}?",
            "league": "Лига: {league}",
            "team": "Клуб: {team}",
            "nationality": "Гражданство: {nationality}",
            "correct": "Верно! Это {player} из {team}. Ты получил {points} очков.",
            "wrong": "Почти! Правильный ответ — {player} из {team}. Завтра будет новая попытка.",
        },
        "pt": {
            "question": "Adivinha o jogador: quem marcou {goals} golos pelo {team}?",
            "league": "Liga: {league}",
            "team": "Clube: {team}",
            "nationality": "Nacionalidade: {nationality}",
            "correct": "Certo! É {player} do {team}. Ganhaste {points} pontos.",
            "wrong": "Quase! A resposta certa é {player} do {team}. Tenta outra vez amanhã.",
        },
    }
    return templates[language][key].format(**values)

def localized_crest_quiz_text(lang: str, key: str, values: dict) -> str:
    language = lang if lang in {"en", "ru", "pt"} else "en"
    templates = {
        "en": {
            "question": "Which club owns this crest?",
            "league": "League: {league}",
            "hint": "Look closely at the colours and shape",
            "pick": "Pick the club name",
            "correct": "Correct! This crest belongs to {team}. You earned {points} points.",
            "wrong": "Almost! This crest belongs to {team}. Try another crest tomorrow.",
        },
        "ru": {
            "question": "Какому клубу принадлежит эта эмблема?",
            "league": "Лига: {league}",
            "hint": "Посмотри внимательно на цвета и форму",
            "pick": "Выбери название клуба",
            "correct": "Верно! Это эмблема клуба {team}. Ты получил {points} очков.",
            "wrong": "Почти! Это эмблема клуба {team}. Завтра будет новая эмблема.",
        },
        "pt": {
            "question": "A que clube pertence este emblema?",
            "league": "Liga: {league}",
            "hint": "Olha bem para as cores e a forma",
            "pick": "Escolhe o nome do clube",
            "correct": "Certo! Este emblema é do {team}. Ganhaste {points} pontos.",
            "wrong": "Quase! Este emblema é do {team}. Tenta outro emblema amanhã.",
        },
    }
    return templates[language][key].format(**values)

async def get_daily_quiz_data(language: str = "en") -> dict:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    league_code = QUIZ_LEAGUE_CODES[stable_number(today, len(QUIZ_LEAGUE_CODES))]
    league = LEAGUES[league_code]
    scorers = []
    try:
        data = await fetch_football_data(f"/competitions/{league_code}/scorers", cache_minutes=60)
        scorers = data.get("scorers", [])
    except Exception as e:
        logger.info(f"Daily quiz scorer source failed for {league_code}: {e}")
    if len(scorers) < 4:
        scorers = FALLBACK_QUIZ_PLAYERS

    valid_scorers = [s for s in scorers if (s.get("player") or {}).get("name")]
    correct = valid_scorers[stable_number(today + league_code, min(len(valid_scorers), 12))]
    correct_player = correct.get("player") or {}
    correct_team = correct.get("team") or {}
    correct_name = correct_player.get("name")
    correct_option = {"id": quiz_option_id(correct_name), "label": correct_name}
    option_names = [correct_name]
    for scorer in valid_scorers:
        name = (scorer.get("player") or {}).get("name")
        if name and name not in option_names:
            option_names.append(name)
        if len(option_names) == 4:
            break
    while len(option_names) < 4:
        for fallback in FALLBACK_QUIZ_PLAYERS:
            name = fallback["player"]["name"]
            if name not in option_names:
                option_names.append(name)
            if len(option_names) == 4:
                break
    options = [{"id": quiz_option_id(name), "label": name} for name in option_names[:4]]
    options.sort(key=lambda option: stable_number(today + option["id"], 1000000))

    values = {
        "goals": correct.get("goals") or 0,
        "team": correct_team.get("shortName") or correct_team.get("name") or "Team",
        "league": league["name"],
        "nationality": correct_player.get("nationality") or "?",
        "player": correct_name,
        "points": QUIZ_REWARD_POINTS,
    }
    return {
        "quizId": f"daily-quiz:{today}:{league_code}",
        "date": today,
        "league": {"code": league_code, "name": league["name"], "emblem": league.get("emblem", "")},
        "question": localized_quiz_text(language, "question", values),
        "hints": [
            localized_quiz_text(language, "league", values),
            localized_quiz_text(language, "team", values),
            localized_quiz_text(language, "nationality", values),
        ],
        "options": options,
        "rewardPoints": QUIZ_REWARD_POINTS,
        "correctOptionId": correct_option["id"],
        "correctPlayer": correct_name,
        "correctTeam": values["team"],
    }

async def get_daily_crest_quiz_data(language: str = "en") -> dict:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    league_code = QUIZ_LEAGUE_CODES[stable_number(today + "crest", len(QUIZ_LEAGUE_CODES))]
    league = LEAGUES[league_code]
    teams = []
    try:
        data = await fetch_football_data(f"/competitions/{league_code}/standings", cache_minutes=60)
        for standing in data.get("standings", []):
            if standing.get("type") == "TOTAL" or not teams:
                teams = [row.get("team") or {} for row in standing.get("table", [])]
                if teams:
                    break
    except Exception as e:
        logger.info(f"Daily crest quiz standings source failed for {league_code}: {e}")
    valid_teams = [team for team in teams if team.get("crest") and (team.get("shortName") or team.get("name"))]
    if len(valid_teams) < 4:
        valid_teams = FALLBACK_QUIZ_TEAMS

    correct = valid_teams[stable_number(today + league_code + "crest", min(len(valid_teams), 12))]
    correct_name = correct.get("shortName") or correct.get("name")
    option_teams = [correct]
    seen_names = {correct_name}
    for team in valid_teams:
        name = team.get("shortName") or team.get("name")
        if name and name not in seen_names:
            option_teams.append(team)
            seen_names.add(name)
        if len(option_teams) == 4:
            break
    while len(option_teams) < 4:
        for fallback in FALLBACK_QUIZ_TEAMS:
            name = fallback.get("shortName") or fallback.get("name")
            if name not in seen_names:
                option_teams.append(fallback)
                seen_names.add(name)
            if len(option_teams) == 4:
                break
    options = [
        {"id": team_quiz_option_id(team), "label": team.get("shortName") or team.get("name")}
        for team in option_teams[:4]
    ]
    options.sort(key=lambda option: stable_number(today + option["id"], 1000000))
    values = {
        "league": league["name"],
        "team": correct_name,
        "points": QUIZ_REWARD_POINTS,
    }
    return {
        "quizId": f"crest-quiz:{today}:{league_code}",
        "date": today,
        "league": {"code": league_code, "name": league["name"], "emblem": league.get("emblem", "")},
        "question": localized_crest_quiz_text(language, "question", values),
        "hints": [
            localized_crest_quiz_text(language, "league", values),
            localized_crest_quiz_text(language, "hint", values),
            localized_crest_quiz_text(language, "pick", values),
        ],
        "crestUrl": correct.get("crest"),
        "options": options,
        "rewardPoints": QUIZ_REWARD_POINTS,
        "correctOptionId": team_quiz_option_id(correct),
        "correctTeam": correct_name,
    }

def calculate_quiz_streak(attempts: list[dict]) -> int:
    answered_dates = sorted({(attempt.get("quizId", "").split(":") + [""])[1] for attempt in attempts if attempt.get("quizId")}, reverse=True)
    if not answered_dates:
        return 0
    streak = 0
    cursor = datetime.now(timezone.utc).date()
    answered_set = set(answered_dates)
    while cursor.isoformat() in answered_set:
        streak += 1
        cursor = cursor - timedelta(days=1)
    return streak

def build_badges(profile: dict, language: str = "en") -> list[dict]:
    lang = language if language in {"en", "ru", "pt"} else "en"
    labels = {
        "en": {
            "first": ("First Kick", "Answer your first daily quiz"),
            "sharp": ("Sharp Shooter", "Get 3 answers right"),
            "streak": ("Three-Day Streak", "Play 3 days in a row"),
            "legend": ("Mini Legend", "Collect 50 points"),
        },
        "ru": {
            "first": ("Первый удар", "Ответь на первую ежедневную викторину"),
            "sharp": ("Меткий удар", "Ответь правильно 3 раза"),
            "streak": ("Серия 3 дня", "Играй 3 дня подряд"),
            "legend": ("Мини-легенда", "Собери 50 очков"),
        },
        "pt": {
            "first": ("Primeiro Remate", "Responde ao primeiro quiz diário"),
            "sharp": ("Pontaria Certa", "Acerta 3 respostas"),
            "streak": ("Sequência de 3 Dias", "Joga 3 dias seguidos"),
            "legend": ("Mini Lenda", "Junta 50 pontos"),
        },
    }
    badge_defs = [
        ("first-kick", "first", "⚽", profile["quizzesPlayed"] >= 1),
        ("sharp-shooter", "sharp", "🎯", profile["correctAnswers"] >= 3),
        ("three-day-streak", "streak", "🔥", profile["currentStreak"] >= 3),
        ("mini-legend", "legend", "🏆", profile["totalPoints"] >= 50),
    ]
    badges = []
    for badge_id, label_key, icon, unlocked in badge_defs:
        title, description = labels[lang][label_key]
        badges.append({"id": badge_id, "title": title, "description": description, "icon": icon, "unlocked": unlocked})
    return badges

async def build_gamification_profile(user_id: str, language: str = "en") -> dict:
    attempts = await db.quiz_attempts.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("answeredAt", -1).to_list(365)
    total_points = sum(int(attempt.get("pointsAwarded", 0)) for attempt in attempts)
    correct_answers = sum(1 for attempt in attempts if attempt.get("isCorrect"))
    current_streak = calculate_quiz_streak(attempts)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    profile = {
        "totalPoints": total_points,
        "quizzesPlayed": len(attempts),
        "correctAnswers": correct_answers,
        "currentStreak": current_streak,
        "todayAnswered": any((attempt.get("quizId", "").split(":") + [""])[1] == today for attempt in attempts),
        "recentAttempts": attempts[:7],
    }
    profile["badges"] = build_badges(profile, language)
    return profile

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

@api_router.get("/matches/{match_id}/story", response_model=MatchStoryResponse)
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
        story = build_story_payload(match)
        if story:
            stories.append(story)
    stories.sort(key=lambda x: x.get("date", ""), reverse=True)
    return stories[:20]

@api_router.get("/gamification/daily-quiz", response_model=DailyQuizResponse)
async def get_daily_quiz(lang: str = "en"):
    quiz = await get_daily_quiz_data(lang)
    return {
        "quizId": quiz["quizId"],
        "date": quiz["date"],
        "league": quiz["league"],
        "question": quiz["question"],
        "hints": quiz["hints"],
        "options": quiz["options"],
        "rewardPoints": quiz["rewardPoints"],
    }

@api_router.get("/gamification/crest-quiz", response_model=DailyCrestQuizResponse)
async def get_daily_crest_quiz(lang: str = "en"):
    quiz = await get_daily_crest_quiz_data(lang)
    return {
        "quizId": quiz["quizId"],
        "date": quiz["date"],
        "league": quiz["league"],
        "question": quiz["question"],
        "hints": quiz["hints"],
        "crestUrl": quiz["crestUrl"],
        "options": quiz["options"],
        "rewardPoints": quiz["rewardPoints"],
    }

@api_router.get("/gamification/profile", response_model=GamificationProfileResponse)
async def get_gamification_profile(request: Request, lang: str = "en"):
    user = await get_current_user(request)
    return await build_gamification_profile(user["_id"], lang)

@api_router.post("/gamification/daily-quiz/answer", response_model=QuizAnswerResponse)
async def answer_daily_quiz(data: QuizAnswerInput, request: Request):
    user = await get_current_user(request)
    quiz = await get_daily_quiz_data(data.language)
    if data.quizId != quiz["quizId"]:
        raise HTTPException(400, "Quiz is no longer active")

    existing = await db.quiz_attempts.find_one(
        {"user_id": user["_id"], "quizId": data.quizId},
        {"_id": 0}
    )
    if existing:
        profile = await build_gamification_profile(user["_id"], data.language)
        explanation_key = "correct" if existing.get("isCorrect") else "wrong"
        explanation = localized_quiz_text(data.language, explanation_key, {
            "player": quiz["correctPlayer"],
            "team": quiz["correctTeam"],
            "points": existing.get("pointsAwarded", 0),
            "goals": 0,
            "league": quiz["league"]["name"],
            "nationality": "",
        })
        return {
            "quizId": data.quizId,
            "selectedOptionId": existing["selectedOptionId"],
            "correctOptionId": existing["correctOptionId"],
            "isCorrect": existing["isCorrect"],
            "pointsAwarded": 0,
            "alreadyAnswered": True,
            "explanation": explanation,
            "profile": profile,
            "badges": profile["badges"],
        }

    is_correct = data.selectedOptionId == quiz["correctOptionId"]
    points_awarded = QUIZ_REWARD_POINTS if is_correct else 2
    attempt_doc = {
        "user_id": user["_id"],
        "quizId": data.quizId,
        "selectedOptionId": data.selectedOptionId,
        "correctOptionId": quiz["correctOptionId"],
        "isCorrect": is_correct,
        "pointsAwarded": points_awarded,
        "answeredAt": datetime.now(timezone.utc).isoformat(),
    }
    await db.quiz_attempts.insert_one(attempt_doc)
    profile = await build_gamification_profile(user["_id"], data.language)
    explanation_key = "correct" if is_correct else "wrong"
    explanation = localized_quiz_text(data.language, explanation_key, {
        "player": quiz["correctPlayer"],
        "team": quiz["correctTeam"],
        "points": points_awarded,
        "goals": 0,
        "league": quiz["league"]["name"],
        "nationality": "",
    })
    return {
        "quizId": data.quizId,
        "selectedOptionId": data.selectedOptionId,
        "correctOptionId": quiz["correctOptionId"],
        "isCorrect": is_correct,
        "pointsAwarded": points_awarded,
        "alreadyAnswered": False,
        "explanation": explanation,
        "profile": profile,
        "badges": profile["badges"],
    }

@api_router.post("/gamification/crest-quiz/answer", response_model=QuizAnswerResponse)
async def answer_daily_crest_quiz(data: QuizAnswerInput, request: Request):
    user = await get_current_user(request)
    quiz = await get_daily_crest_quiz_data(data.language)
    if data.quizId != quiz["quizId"]:
        raise HTTPException(400, "Quiz is no longer active")

    existing = await db.quiz_attempts.find_one(
        {"user_id": user["_id"], "quizId": data.quizId},
        {"_id": 0}
    )
    if existing:
        profile = await build_gamification_profile(user["_id"], data.language)
        explanation_key = "correct" if existing.get("isCorrect") else "wrong"
        explanation = localized_crest_quiz_text(data.language, explanation_key, {
            "team": quiz["correctTeam"],
            "league": quiz["league"]["name"],
            "points": existing.get("pointsAwarded", 0),
        })
        return {
            "quizId": data.quizId,
            "selectedOptionId": existing["selectedOptionId"],
            "correctOptionId": existing["correctOptionId"],
            "isCorrect": existing["isCorrect"],
            "pointsAwarded": 0,
            "alreadyAnswered": True,
            "explanation": explanation,
            "profile": profile,
            "badges": profile["badges"],
        }

    is_correct = data.selectedOptionId == quiz["correctOptionId"]
    points_awarded = QUIZ_REWARD_POINTS if is_correct else 2
    attempt_doc = {
        "user_id": user["_id"],
        "quizId": data.quizId,
        "selectedOptionId": data.selectedOptionId,
        "correctOptionId": quiz["correctOptionId"],
        "isCorrect": is_correct,
        "pointsAwarded": points_awarded,
        "answeredAt": datetime.now(timezone.utc).isoformat(),
    }
    await db.quiz_attempts.insert_one(attempt_doc)
    profile = await build_gamification_profile(user["_id"], data.language)
    explanation_key = "correct" if is_correct else "wrong"
    explanation = localized_crest_quiz_text(data.language, explanation_key, {
        "team": quiz["correctTeam"],
        "league": quiz["league"]["name"],
        "points": points_awarded,
    })
    return {
        "quizId": data.quizId,
        "selectedOptionId": data.selectedOptionId,
        "correctOptionId": quiz["correctOptionId"],
        "isCorrect": is_correct,
        "pointsAwarded": points_awarded,
        "alreadyAnswered": False,
        "explanation": explanation,
        "profile": profile,
        "badges": profile["badges"],
    }

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
    await db.match_stories.create_index([("matchId", 1), ("language", 1)], unique=True)
    await db.quiz_attempts.create_index([("user_id", 1), ("quizId", 1)], unique=True)
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
