import os

import pytest
import requests


# Admin diagnostics API regression tests for auth gating, diagnostics listing, refresh, and public story isolation
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL")

if not BASE_URL:
    pytest.skip("REACT_APP_BACKEND_URL is not set", allow_module_level=True)

BASE_URL = BASE_URL.rstrip("/")


@pytest.fixture(scope="session")
def admin_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@example.com", "password": "admin123"},
        timeout=30,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "admin@example.com"
    assert payload["role"] == "admin"
    return session


@pytest.fixture(scope="session")
def user_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    email = f"test_admin_diag_user_{os.urandom(4).hex()}@example.com"
    register_response = session.post(
        f"{BASE_URL}/api/auth/register",
        json={"name": "TEST Admin Diag User", "email": email, "password": "admin123"},
        timeout=30,
    )
    assert register_response.status_code == 200
    return session


def test_admin_login_exposes_admin_role(admin_client):
    response = admin_client.get(f"{BASE_URL}/api/auth/me", timeout=30)
    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "admin@example.com"
    assert payload["role"] == "admin"


def test_story_diagnostics_requires_admin_auth():
    anon_session = requests.Session()
    anon_session.headers.update({"Content-Type": "application/json"})

    anon_response = anon_session.get(
        f"{BASE_URL}/api/admin/story-diagnostics",
        params={"lang": "ru", "limit": 3},
        timeout=30,
    )
    assert anon_response.status_code == 401


def test_story_diagnostics_forbidden_for_regular_user(user_client):
    response = user_client.get(
        f"{BASE_URL}/api/admin/story-diagnostics",
        params={"lang": "ru", "limit": 3},
        timeout=30,
    )
    assert response.status_code == 403


def test_get_story_diagnostics_admin_shape(admin_client):
    response = admin_client.get(
        f"{BASE_URL}/api/admin/story-diagnostics",
        params={"lang": "ru", "limit": 3},
        timeout=45,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["language"] == "ru"
    assert isinstance(payload["matches"], list)
    assert len(payload["matches"]) <= 3

    if not payload["matches"]:
        pytest.skip("No finished matches available for diagnostics")

    first = payload["matches"][0]
    assert isinstance(first["matchId"], int)
    assert first["status"] == "FINISHED"
    assert first["storyStatus"] in {"not_checked", "fallback", "source_found"}
    assert isinstance(first["diagnostics"], list)
    assert isinstance(first.get("sourceSnippets"), list)


def test_refresh_story_diagnostics_and_public_story_safety(admin_client):
    list_response = admin_client.get(
        f"{BASE_URL}/api/admin/story-diagnostics",
        params={"lang": "ru", "limit": 3},
        timeout=45,
    )
    assert list_response.status_code == 200
    matches = list_response.json().get("matches", [])
    if not matches:
        pytest.skip("No finished matches available to refresh diagnostics")

    match_id = matches[0]["matchId"]

    refresh_response = admin_client.post(
        f"{BASE_URL}/api/admin/story-diagnostics/{match_id}/refresh",
        params={"lang": "ru"},
        timeout=75,
    )
    assert refresh_response.status_code == 200
    refresh_payload = refresh_response.json()

    assert refresh_payload["matchId"] == match_id
    assert refresh_payload["language"] == "ru"
    assert refresh_payload["status"] == "FINISHED"
    assert refresh_payload["storyStatus"] in {"fallback", "source_found"}
    assert isinstance(refresh_payload["diagnostics"], list)
    assert len(refresh_payload["diagnostics"]) > 0
    assert isinstance(refresh_payload.get("sourceSnippets"), list)
    for snippet in refresh_payload["sourceSnippets"]:
        assert isinstance(snippet.get("title"), str) and snippet["title"].strip()
        assert isinstance(snippet.get("description"), str) and snippet["description"].strip()
        assert isinstance(snippet.get("url"), str) and snippet["url"].startswith("http")

    providers = {item.get("provider") for item in refresh_payload["diagnostics"]}
    expected_provider_ids = {"official_content", "rss", "newsapi", "newsdata", "gnews"}
    assert expected_provider_ids.issubset(providers)

    for item in refresh_payload["diagnostics"]:
        assert item.get("status") in {"matched", "failed", "no_match", "no_results", "skipped", "fallback"}
        assert isinstance(item.get("queryCount", 0), int)
        assert isinstance(item.get("candidateCount", 0), int)
        assert isinstance(item.get("matchedCount", 0), int)

    public_story_response = admin_client.get(
        f"{BASE_URL}/api/matches/{match_id}/story",
        params={"lang": "ru"},
        timeout=75,
    )
    assert public_story_response.status_code == 200
    public_story = public_story_response.json()
    assert public_story["matchId"] == match_id
    assert public_story["language"] == "ru"
    assert "diagnostics" not in public_story
    assert isinstance(public_story.get("sources"), list)
    assert isinstance(public_story.get("summary"), str) and public_story["summary"].strip()
