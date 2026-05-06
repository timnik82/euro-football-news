import asyncio
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional
import httpx
from config import logger

GNEWS_RATE_LIMIT_LOCK = asyncio.Lock()
GNEWS_RATE_LIMIT_STATE = {"last_request_at": 0.0}

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
