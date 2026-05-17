from datetime import datetime, timezone

from config import MATCH_STORY_CACHE_VERSION
from database import db
from football_service import fetch_football_data
from match_story_builder import build_child_match_story
from match_story_sources import fetch_news_articles_for_match


def normalize_story_language(language: str) -> str:
    return language if language in {"en", "ru", "pt"} else "en"


async def get_cached_match_story(match_id: int, language: str):
    return await db.match_stories.find_one(
        {"matchId": match_id, "language": normalize_story_language(language)},
        {"_id": 0},
    )


async def build_and_cache_match_story(match_id: int, language: str):
    story_language = normalize_story_language(language)
    match_data = await fetch_football_data(f"/matches/{match_id}", cache_minutes=10)
    diagnostics = []
    articles = []
    if match_data.get("status") == "FINISHED":
        articles = await fetch_news_articles_for_match(match_data, story_language, diagnostics)
    else:
        diagnostics.append({
            "provider": "match_status",
            "sourceName": "Match status",
            "status": "skipped",
            "message": "External story search runs only after the match is finished",
            "queryCount": 0,
            "candidateCount": 0,
            "matchedCount": 0,
        })
    story_body = build_child_match_story(match_data, story_language, articles)
    story_doc = {
        "matchId": match_id,
        "language": story_language,
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
        "diagnostics": diagnostics,
    }
    await db.match_stories.update_one(
        {"matchId": match_id, "language": story_language},
        {"$set": story_doc},
        upsert=True,
    )
    return story_doc