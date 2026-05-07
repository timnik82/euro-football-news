import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional

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
