import os
import time

import pytest
import requests


# Story + match detail regression tests for match-specific educational story feature
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL")

if not BASE_URL:
    pytest.skip("REACT_APP_BACKEND_URL is not set", allow_module_level=True)

BASE_URL = BASE_URL.rstrip("/")


@pytest.fixture(scope="session")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="session")
def sample_match_id(api_client):
    response = api_client.get(f"{BASE_URL}/api/stories", timeout=30)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    match_id = data[0].get("match_id")
    assert isinstance(match_id, int)
    return match_id


def _assert_story_shape(payload, expected_match_id, expected_lang):
    assert payload["matchId"] == expected_match_id
    assert payload["language"] == expected_lang
    assert isinstance(payload["title"], str) and payload["title"].strip()
    assert isinstance(payload["summary"], str) and payload["summary"].strip()
    assert isinstance(payload["keyPoints"], list)
    assert 1 <= len(payload["keyPoints"]) <= 5
    assert isinstance(payload["whyItMatters"], str) and payload["whyItMatters"].strip()
    assert isinstance(payload["isFallback"], bool)
    assert "generatedAt" in payload and isinstance(payload["generatedAt"], str)

    assert "imageUrl" in payload
    assert "videoUrl" in payload
    assert isinstance(payload["sources"], list)

    for src in payload["sources"]:
        assert isinstance(src.get("title"), str) and src["title"].strip()
        assert isinstance(src.get("url"), str) and src["url"].startswith("http")


def test_stories_endpoint_still_works(api_client):
    response = api_client.get(f"{BASE_URL}/api/stories", timeout=30)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    first = data[0]
    assert isinstance(first.get("match_id"), int)
    assert isinstance(first.get("home_team"), dict)
    assert isinstance(first.get("away_team"), dict)
    assert isinstance(first.get("score"), dict)


def test_match_detail_endpoint_still_works(api_client, sample_match_id):
    response = api_client.get(f"{BASE_URL}/api/matches/{sample_match_id}", timeout=30)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == sample_match_id
    assert isinstance(data.get("homeTeam"), dict)
    assert isinstance(data.get("awayTeam"), dict)
    assert isinstance(data.get("score"), dict)


@pytest.mark.parametrize(
    "lang,title_prefix",
    [
        ("en", "Story of the Match"),
        ("ru", "История матча"),
        ("pt", "História do jogo"),
    ],
)
def test_match_story_language_variants(api_client, sample_match_id, lang, title_prefix):
    response = api_client.get(
        f"{BASE_URL}/api/matches/{sample_match_id}/story",
        params={"lang": lang},
        timeout=45,
    )
    assert response.status_code == 200

    payload = response.json()
    _assert_story_shape(payload, sample_match_id, lang)
    assert payload["title"].startswith(title_prefix)


def test_match_story_cache_stability(api_client, sample_match_id):
    params = {"lang": "en"}

    start_1 = time.perf_counter()
    response_1 = api_client.get(
        f"{BASE_URL}/api/matches/{sample_match_id}/story",
        params=params,
        timeout=45,
    )
    duration_1 = time.perf_counter() - start_1
    assert response_1.status_code == 200
    payload_1 = response_1.json()

    time.sleep(0.2)

    start_2 = time.perf_counter()
    response_2 = api_client.get(
        f"{BASE_URL}/api/matches/{sample_match_id}/story",
        params=params,
        timeout=45,
    )
    duration_2 = time.perf_counter() - start_2
    assert response_2.status_code == 200
    payload_2 = response_2.json()

    _assert_story_shape(payload_1, sample_match_id, "en")
    _assert_story_shape(payload_2, sample_match_id, "en")

    assert payload_2["title"] == payload_1["title"]
    assert payload_2["summary"] == payload_1["summary"]
    assert payload_2["keyPoints"] == payload_1["keyPoints"]
    assert payload_2["whyItMatters"] == payload_1["whyItMatters"]
    assert payload_2["isFallback"] == payload_1["isFallback"]
    assert payload_2["generatedAt"] == payload_1["generatedAt"]

    assert duration_2 <= duration_1 + 0.75
