from match_story_builder import build_child_match_story
from match_story_sources import (
    configured_content_sources,
    configured_rss_feeds,
    fetch_news_articles_for_match,
    fetch_official_content_articles_for_match,
    fetch_rss_articles_for_match,
    parse_official_content_articles,
    parse_rss_articles,
)
from match_story_utils import (
    article_relevance_score,
    build_match_queries,
    clean_text,
    contains_any,
    normalize_article_payload,
    parse_article_date,
    provider_safe_query,
    strip_html,
    team_aliases,
)

__all__ = [
    "article_relevance_score",
    "build_child_match_story",
    "build_match_queries",
    "clean_text",
    "configured_content_sources",
    "configured_rss_feeds",
    "contains_any",
    "fetch_news_articles_for_match",
    "fetch_official_content_articles_for_match",
    "fetch_rss_articles_for_match",
    "normalize_article_payload",
    "parse_article_date",
    "parse_official_content_articles",
    "parse_rss_articles",
    "provider_safe_query",
    "strip_html",
    "team_aliases",
]
