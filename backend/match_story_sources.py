import asyncio
import json
import os
import time
import xml.etree.ElementTree as ET
from typing import Optional
import httpx
from config import logger
from match_story_utils import (
    article_relevance_score,
    build_match_queries,
    normalize_article_payload,
    parse_article_date,
    provider_safe_query,
    strip_html,
)

GNEWS_RATE_LIMIT_LOCK = asyncio.Lock()
GNEWS_RATE_LIMIT_STATE = {"last_request_at": 0.0}

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
