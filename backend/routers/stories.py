from datetime import datetime, timezone, timedelta
from fastapi import APIRouter
from config import COMPETITIONS, MATCH_STORY_CACHE_VERSION
from football_service import build_story_payload, fetch_football_data
from match_story_cache_service import build_and_cache_match_story, get_cached_match_story, normalize_story_language
from schemas import MatchStoryResponse

router = APIRouter(tags=["stories"])

@router.get("/matches/{match_id}/story", response_model=MatchStoryResponse)
async def get_match_story(match_id: int, lang: str = "en", refresh: bool = False):
    language = normalize_story_language(lang)
    cached_story = await get_cached_match_story(match_id, language)
    if not refresh and cached_story and cached_story.get("cacheVersion") == MATCH_STORY_CACHE_VERSION:
        return cached_story
    return await build_and_cache_match_story(match_id, language)

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
