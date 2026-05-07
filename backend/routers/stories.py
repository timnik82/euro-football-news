from datetime import datetime, timezone, timedelta
from fastapi import APIRouter
from config import COMPETITIONS, MATCH_STORY_CACHE_VERSION
from database import db
from football_service import build_story_payload, fetch_football_data
from match_story_builder import build_child_match_story
from match_story_sources import fetch_news_articles_for_match
from schemas import MatchStoryResponse

router = APIRouter(tags=["stories"])

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
