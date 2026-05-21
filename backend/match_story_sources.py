import asyncio
import html
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from typing import Optional
import httpx
from dotenv import dotenv_values
from config import ROOT_DIR, logger
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
SOURCE_ENV_CACHE = None

PROVIDER_LABELS = {
    "official_content": "Official content",
    "official_page": "Official league page",
    "rss": "RSS feed",
    "newsapi": "NewsAPI.org",
    "newsdata": "NewsData.io",
    "gnews": "GNews",
}

def add_provider_diagnostic(
    diagnostics: Optional[list[dict]],
    provider: str,
    status: str,
    source_name: Optional[str] = None,
    message: str = "",
    http_status: Optional[int] = None,
    query_count: int = 0,
    candidate_count: int = 0,
    matched_count: int = 0,
    error: Optional[str] = None,
):
    if diagnostics is None:
        return
    entry = {
        "provider": provider,
        "sourceName": source_name or PROVIDER_LABELS.get(provider, provider),
        "status": status,
        "message": message,
        "queryCount": query_count,
        "candidateCount": candidate_count,
        "matchedCount": matched_count,
    }
    if http_status is not None:
        entry["httpStatus"] = http_status
    if error:
        entry["error"] = error[:240]
    diagnostics.append(entry)

def source_env_value(key: str) -> Optional[str]:
    global SOURCE_ENV_CACHE
    value = os.environ.get(key)
    if value:
        return value
    if SOURCE_ENV_CACHE is None:
        SOURCE_ENV_CACHE = dotenv_values(ROOT_DIR / ".env")
    return SOURCE_ENV_CACHE.get(key)

async def wait_for_gnews_slot():
    async with GNEWS_RATE_LIMIT_LOCK:
        elapsed = time.monotonic() - GNEWS_RATE_LIMIT_STATE["last_request_at"]
        if elapsed < 1.6:
            await asyncio.sleep(1.6 - elapsed)
        GNEWS_RATE_LIMIT_STATE["last_request_at"] = time.monotonic()

def configured_rss_feeds() -> list[dict]:
    raw_feeds = source_env_value("MATCH_REPORT_RSS_FEEDS")
    if not raw_feeds:
        return []
    try:
        feeds = json.loads(raw_feeds)
        return [feed for feed in feeds if feed.get("name") and feed.get("url")]
    except Exception as e:
        logger.info(f"RSS feed config invalid: {e}")
        return []

def configured_content_sources() -> list[dict]:
    raw_sources = source_env_value("MATCH_REPORT_CONTENT_SOURCES")
    if not raw_sources:
        return []
    try:
        sources = json.loads(raw_sources)
        return [source for source in sources if source.get("name") and source.get("url")]
    except Exception as e:
        logger.info(f"Content source config invalid: {e}")
        return []

def configured_page_sources() -> list[dict]:
    raw_sources = source_env_value("MATCH_REPORT_PAGE_SOURCES")
    if not raw_sources:
        return []
    try:
        sources = json.loads(raw_sources)
        return [source for source in sources if source.get("name") and source.get("url")]
    except Exception as e:
        logger.info(f"Page source config invalid: {e}")
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

async def fetch_rss_articles_for_match(match: dict, diagnostics: Optional[list[dict]] = None) -> list[dict]:
    feeds = configured_rss_feeds()
    if not feeds:
        add_provider_diagnostic(diagnostics, "rss", "skipped", message="No RSS feeds configured")
        return []
    articles = []
    seen_urls = set()
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers={"User-Agent": "GoalKickKidApp/1.0"}) as http:
        for feed in feeds:
            try:
                resp = await http.get(feed["url"])
                if resp.status_code != 200:
                    logger.info(f"RSS feed {feed['name']} returned {resp.status_code}")
                    add_provider_diagnostic(
                        diagnostics,
                        "rss",
                        "failed",
                        source_name=feed["name"],
                        message="Feed request returned a non-200 status",
                        http_status=resp.status_code,
                    )
                    continue
                parsed_articles = parse_rss_articles(resp.text, feed["name"])
                matched_count = 0
                for article in parsed_articles:
                    if article["url"] in seen_urls:
                        continue
                    relevance = article_relevance_score(article, match)
                    if relevance >= 9:
                        article["relevanceScore"] = relevance + 2
                        articles.append(article)
                        seen_urls.add(article["url"])
                        matched_count += 1
                add_provider_diagnostic(
                    diagnostics,
                    "rss",
                    "matched" if matched_count else "no_match",
                    source_name=feed["name"],
                    message="RSS feed checked for exact match reports",
                    http_status=resp.status_code,
                    candidate_count=len(parsed_articles),
                    matched_count=matched_count,
                )
            except Exception as e:
                logger.info(f"RSS feed {feed['name']} failed: {e}")
                add_provider_diagnostic(
                    diagnostics,
                    "rss",
                    "failed",
                    source_name=feed.get("name"),
                    message="Feed request or parsing failed",
                    error=str(e),
                )
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

def json_walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from json_walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from json_walk(child)

def page_source_article_url(item: dict, source: dict) -> str:
    raw_url = item.get("url") or item.get("link") or item.get("href") or item.get("path")
    slug = item.get("slug") or item.get("titleUrlSegment")
    base_url = source.get("baseUrl") or source["url"]
    if raw_url:
        if str(raw_url).startswith("http"):
            return raw_url
        return f"{base_url.rstrip('/')}/{str(raw_url).lstrip('/')}"
    if slug and source.get("urlPrefix"):
        return f"{base_url.rstrip('/')}/{source['urlPrefix'].strip('/')}/{str(slug).strip('/')}"
    return ""

def nested_image_url(item: dict) -> Optional[str]:
    image = item.get("image") or item.get("cover") or item.get("thumbnail")
    if isinstance(image, dict):
        return image.get("url") or (image.get("resizes") or {}).get("medium") or (image.get("resizes") or {}).get("large")
    if isinstance(image, str):
        return image
    return item.get("imageUrl") or item.get("image_url")

def parse_next_data_articles(html_text: str, source: dict) -> list[dict]:
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_text, re.S)
    if not match:
        return []
    try:
        payload = json.loads(html.unescape(match.group(1)))
    except Exception as e:
        logger.info(f"Next data parse failed for {source['name']}: {e}")
        return []
    articles = []
    seen_urls = set()
    for item in json_walk(payload):
        title = item.get("title") or item.get("headline") or item.get("name")
        url = page_source_article_url(item, source)
        if not title or not url or url in seen_urls:
            continue
        if re.search(r"\.(jpe?g|png|webp|gif|svg)(\?|$)", url, re.I):
            continue
        description = item.get("description") or item.get("summary") or item.get("excerpt") or item.get("subtitle") or item.get("lead")
        normalized = normalize_article_payload("official_page", {
            "title": title,
            "url": url,
            "description": strip_html(description or ""),
            "publishedAt": item.get("publishedAt") or item.get("date") or item.get("publicationDate"),
            "imageUrl": nested_image_url(item),
            "sourceName": source["name"],
        })
        if normalized:
            articles.append(normalized)
            seen_urls.add(url)
        if len(articles) >= int(source.get("limit", 25)):
            break
    return articles

def parse_meta_content(html_text: str, names: list[str]) -> Optional[str]:
    for name in names:
        pattern = rf'<meta[^>]+(?:name|property)=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']'
        match = re.search(pattern, html_text, re.I)
        if match:
            return html.unescape(match.group(1))
        reverse_pattern = rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:name|property)=["\']{re.escape(name)}["\']'
        match = re.search(reverse_pattern, html_text, re.I)
        if match:
            return html.unescape(match.group(1))
    return None

async def enrich_page_article(http: httpx.AsyncClient, article: dict) -> dict:
    if article.get("description") and article.get("imageUrl"):
        return article
    try:
        resp = await http.get(article["url"])
        if resp.status_code != 200:
            return article
        text = resp.text
        article["description"] = article.get("description") or strip_html(parse_meta_content(text, ["description", "og:description", "twitter:description"]) or "")[:320]
        article["imageUrl"] = article.get("imageUrl") or parse_meta_content(text, ["og:image", "twitter:image"])
        article["publishedAt"] = article.get("publishedAt") or parse_meta_content(text, ["article:published_time"])
    except Exception as e:
        logger.info(f"Official page detail enrichment failed for {article.get('url')}: {e}")
    return article

async def fetch_official_page_articles_for_match(match: dict, diagnostics: Optional[list[dict]] = None) -> list[dict]:
    sources = configured_page_sources()
    if not sources:
        add_provider_diagnostic(diagnostics, "official_page", "skipped", message="No official page sources configured")
        return []
    articles = []
    seen_urls = set()
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers={"User-Agent": "GoalKickKidApp/1.0"}) as http:
        for source in sources:
            try:
                resp = await http.get(source["url"])
                if resp.status_code != 200:
                    add_provider_diagnostic(
                        diagnostics,
                        "official_page",
                        "failed",
                        source_name=source["name"],
                        message="Official page returned a non-200 status",
                        http_status=resp.status_code,
                    )
                    continue
                parsed_articles = parse_next_data_articles(resp.text, source)
                enriched_articles = []
                for article in parsed_articles[: int(source.get("detailLimit", 12))]:
                    enriched_articles.append(await enrich_page_article(http, article))
                parsed_articles = enriched_articles + parsed_articles[int(source.get("detailLimit", 12)):]
                matched_count = 0
                for article in parsed_articles:
                    if article["url"] in seen_urls:
                        continue
                    relevance = article_relevance_score(article, match)
                    if relevance >= 9:
                        article["relevanceScore"] = relevance + 3
                        articles.append(article)
                        seen_urls.add(article["url"])
                        matched_count += 1
                add_provider_diagnostic(
                    diagnostics,
                    "official_page",
                    "matched" if matched_count else "no_match" if parsed_articles else "no_results",
                    source_name=source["name"],
                    message="Official page JSON/metadata checked for exact match reports",
                    http_status=resp.status_code,
                    candidate_count=len(parsed_articles),
                    matched_count=matched_count,
                )
            except Exception as e:
                logger.info(f"Official page source {source['name']} failed: {e}")
                add_provider_diagnostic(
                    diagnostics,
                    "official_page",
                    "failed",
                    source_name=source.get("name"),
                    message="Official page request or parsing failed",
                    error=str(e),
                )
    articles.sort(key=lambda a: (a.get("relevanceScore", 0), 1 if a.get("imageUrl") else 0, a.get("publishedAt") or ""), reverse=True)
    for article in articles:
        article.pop("relevanceScore", None)
    return articles[:5]

async def fetch_official_content_articles_for_match(match: dict, diagnostics: Optional[list[dict]] = None) -> list[dict]:
    sources = configured_content_sources()
    if not sources:
        add_provider_diagnostic(diagnostics, "official_content", "skipped", message="No official content sources configured")
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
                    add_provider_diagnostic(
                        diagnostics,
                        "official_content",
                        "failed",
                        source_name=source["name"],
                        message="Official source returned a non-200 status",
                        http_status=resp.status_code,
                    )
                    continue
                parsed_articles = parse_official_content_articles(resp.json(), source["name"])
                matched_count = 0
                for article in parsed_articles:
                    if article["url"] in seen_urls:
                        continue
                    relevance = article_relevance_score(article, match)
                    if relevance >= 9:
                        article["relevanceScore"] = relevance + 4
                        articles.append(article)
                        seen_urls.add(article["url"])
                        matched_count += 1
                add_provider_diagnostic(
                    diagnostics,
                    "official_content",
                    "matched" if matched_count else "no_match",
                    source_name=source["name"],
                    message="Official source checked for exact match reports",
                    http_status=resp.status_code,
                    candidate_count=len(parsed_articles),
                    matched_count=matched_count,
                )
            except Exception as e:
                logger.info(f"Official content source {source['name']} failed: {e}")
                add_provider_diagnostic(
                    diagnostics,
                    "official_content",
                    "failed",
                    source_name=source.get("name"),
                    message="Official source request or parsing failed",
                    error=str(e),
                )
    articles.sort(key=lambda a: (a.get("relevanceScore", 0), 1 if a.get("imageUrl") else 0, a.get("publishedAt") or ""), reverse=True)
    for article in articles:
        article.pop("relevanceScore", None)
    return articles[:5]

async def fetch_news_articles_for_match(match: dict, language: str, diagnostics: Optional[list[dict]] = None) -> list[dict]:
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
    articles = await fetch_official_content_articles_for_match(match, diagnostics)
    page_articles = await fetch_official_page_articles_for_match(match, diagnostics)
    articles.extend([article for article in page_articles if article["url"] not in {item["url"] for item in articles}])
    rss_articles = await fetch_rss_articles_for_match(match, diagnostics)
    articles.extend([article for article in rss_articles if article["url"] not in {item["url"] for item in articles}])
    seen_urls = {article["url"] for article in articles}
    provider_totals = {
        provider["name"]: {
            "attempts": 0,
            "candidateCount": 0,
            "matchedCount": 0,
            "httpStatuses": [],
            "errors": [],
            "hasKey": bool(provider["key"]),
        }
        for provider in provider_configs
    }

    async with httpx.AsyncClient(timeout=7.0) as http:
        for query_index, query in enumerate(queries):
            for provider in provider_configs:
                if not provider["key"]:
                    continue
                if provider["name"] == "gnews" and query_index >= 2:
                    continue
                total = provider_totals[provider["name"]]
                total["attempts"] += 1
                try:
                    safe_query = provider_safe_query(query, provider["name"])
                    if provider["name"] == "gnews":
                        await wait_for_gnews_slot()
                    resp = await http.get(
                        provider["url"],
                        params=provider["params"](safe_query),
                        headers=provider["headers"](),
                    )
                    total["httpStatuses"].append(resp.status_code)
                    if resp.status_code != 200:
                        logger.info(f"News provider {provider['name']} returned {resp.status_code}")
                        continue
                    payload = resp.json()
                    raw_articles = provider["extract"](payload)
                    total["candidateCount"] += len(raw_articles)
                    for raw_article in raw_articles:
                        normalized = normalize_article_payload(provider["name"], raw_article)
                        if not normalized or normalized["url"] in seen_urls:
                            continue
                        relevance = article_relevance_score(normalized, match)
                        if relevance >= 9:
                            normalized["relevanceScore"] = relevance
                            articles.append(normalized)
                            seen_urls.add(normalized["url"])
                            total["matchedCount"] += 1
                except Exception as e:
                    logger.info(f"News provider {provider['name']} failed: {e}")
                    provider_totals[provider["name"]]["errors"].append(str(e))

    for provider in provider_configs:
        total = provider_totals[provider["name"]]
        if not total["hasKey"]:
            add_provider_diagnostic(
                diagnostics,
                provider["name"],
                "skipped",
                source_name=PROVIDER_LABELS.get(provider["name"]),
                message="API key is not configured",
            )
            continue
        if total["matchedCount"] > 0:
            status = "matched"
            message = "Provider returned at least one exact match report"
        elif total["errors"] or any(code >= 400 for code in total["httpStatuses"]):
            status = "failed"
            message = "Provider request failed or returned an error status"
        elif total["candidateCount"] > 0:
            status = "no_match"
            message = "Provider returned articles, but none matched the exact fixture"
        else:
            status = "no_results"
            message = "Provider returned no usable articles for these queries"
        add_provider_diagnostic(
            diagnostics,
            provider["name"],
            status,
            source_name=PROVIDER_LABELS.get(provider["name"]),
            message=message,
            http_status=total["httpStatuses"][-1] if total["httpStatuses"] else None,
            query_count=total["attempts"],
            candidate_count=total["candidateCount"],
            matched_count=total["matchedCount"],
            error="; ".join(total["errors"][:2]) if total["errors"] else None,
        )

    articles.sort(key=lambda a: (a.get("relevanceScore", 0), 1 if a.get("imageUrl") else 0, a.get("publishedAt") or ""), reverse=True)
    for article in articles:
        article.pop("relevanceScore", None)
    return articles[:5]
