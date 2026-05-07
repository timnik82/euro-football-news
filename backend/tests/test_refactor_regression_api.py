import os
import uuid

import pytest
import requests


# Backend refactor regression tests: auth, favorites, football, and gamification core routes
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
def auth_client(api_client):
    login_payload = {"email": "admin@example.com", "password": "admin123"}
    response = api_client.post(f"{BASE_URL}/api/auth/login", json=login_payload, timeout=30)
    assert response.status_code == 200
    data = response.json()
    assert data.get("email") == "admin@example.com"
    assert isinstance(data.get("_id"), str)
    return api_client


def test_auth_login_sets_httponly_cookies(api_client):
    response = api_client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@example.com", "password": "admin123"},
        timeout=30,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "admin@example.com"
    assert payload["role"] == "admin"

    set_cookie = "; ".join(response.headers.get("set-cookie", "").split(","))
    assert "access_token=" in set_cookie
    assert "refresh_token=" in set_cookie
    assert "HttpOnly" in set_cookie


def test_auth_me_works_with_cookie_session(auth_client):
    response = auth_client.get(f"{BASE_URL}/api/auth/me", timeout=30)
    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "admin@example.com"
    assert payload["role"] == "admin"
    assert "password_hash" not in payload


def test_auth_cors_allows_credentials_for_explicit_origin(api_client):
    origin = os.environ.get("FRONTEND_ORIGIN", "https://young-fan-portal.preview.emergentagent.com")
    cors_base_url = os.environ.get("BACKEND_INTERNAL_URL", "http://localhost:8001").rstrip("/")
    response = api_client.options(
        f"{cors_base_url}/api/auth/login",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
        timeout=30,
    )
    assert response.status_code in (200, 204)
    assert response.headers.get("access-control-allow-origin") == origin
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_auth_bruteforce_lockout_after_five_failures(api_client):
    email = f"test_lockout_{uuid.uuid4().hex[:10]}@example.com"
    register_response = api_client.post(
        f"{BASE_URL}/api/auth/register",
        json={"name": "TEST Lockout", "email": email, "password": "admin123"},
        timeout=30,
    )
    assert register_response.status_code == 200

    for _ in range(5):
        failed = api_client.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": "wrong-password"},
            timeout=30,
        )
        assert failed.status_code == 401

    post_threshold = api_client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": "admin123"},
        timeout=30,
    )

    assert post_threshold.status_code in (423, 429, 401)
    if post_threshold.status_code == 401:
        detail = str(post_threshold.json()).lower()
        assert "lock" in detail or "too many" in detail


def test_favorites_get_authenticated(auth_client):
    response = auth_client.get(f"{BASE_URL}/api/favorites", timeout=30)
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)


def test_football_leagues_and_today_match_routes(api_client):
    leagues_response = api_client.get(f"{BASE_URL}/api/leagues", timeout=30)
    assert leagues_response.status_code == 200
    leagues = leagues_response.json()
    assert isinstance(leagues, list)
    assert len(leagues) > 0
    assert isinstance(leagues[0].get("code"), str)

    today_response = api_client.get(f"{BASE_URL}/api/matches/today", timeout=45)
    assert today_response.status_code == 200
    today = today_response.json()
    assert isinstance(today, list)


def test_search_endpoint_returns_structured_results(api_client):
    response = api_client.get(f"{BASE_URL}/api/search", params={"q": "ar"}, timeout=45)
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload.get("teams"), list)
    assert isinstance(payload.get("players"), list)


@pytest.fixture(scope="session")
def sample_match_id(api_client):
    stories_response = api_client.get(f"{BASE_URL}/api/stories", timeout=45)
    assert stories_response.status_code == 200
    stories = stories_response.json()
    assert isinstance(stories, list)
    if stories and isinstance(stories[0].get("match_id"), int):
        return stories[0]["match_id"]

    today_response = api_client.get(f"{BASE_URL}/api/matches/today", timeout=45)
    assert today_response.status_code == 200
    today_matches = today_response.json()
    if not today_matches:
        pytest.skip("No available matches from stories or today's feed")
    return today_matches[0]["id"]


def test_stories_match_detail_and_story_lang_ru(api_client, sample_match_id):
    stories_response = api_client.get(f"{BASE_URL}/api/stories", timeout=45)
    assert stories_response.status_code == 200
    stories = stories_response.json()
    assert isinstance(stories, list)

    match_response = api_client.get(f"{BASE_URL}/api/matches/{sample_match_id}", timeout=45)
    assert match_response.status_code == 200
    match_payload = match_response.json()
    assert match_payload["id"] == sample_match_id
    assert isinstance(match_payload.get("homeTeam"), dict)
    assert isinstance(match_payload.get("awayTeam"), dict)

    story_response = api_client.get(
        f"{BASE_URL}/api/matches/{sample_match_id}/story",
        params={"lang": "ru"},
        timeout=60,
    )
    assert story_response.status_code == 200
    story_payload = story_response.json()
    assert story_payload["matchId"] == sample_match_id
    assert story_payload["language"] == "ru"
    assert isinstance(story_payload.get("title"), str) and story_payload["title"].strip()


def test_gamification_quizzes_shape_and_hidden_answers(api_client):
    daily_response = api_client.get(f"{BASE_URL}/api/gamification/daily-quiz", params={"lang": "ru"}, timeout=45)
    assert daily_response.status_code == 200
    daily = daily_response.json()
    assert isinstance(daily.get("quizId"), str)
    assert isinstance(daily.get("options"), list) and len(daily["options"]) == 4
    assert "correctOptionId" not in daily

    crest_response = api_client.get(f"{BASE_URL}/api/gamification/crest-quiz", params={"lang": "ru"}, timeout=45)
    assert crest_response.status_code == 200
    crest = crest_response.json()
    assert isinstance(crest.get("quizId"), str)
    assert isinstance(crest.get("options"), list) and len(crest["options"]) == 4
    assert "correctOptionId" not in crest


def test_gamification_profile_auth_and_duplicate_protection(api_client, auth_client):
    unauth_session = requests.Session()
    unauth_session.headers.update({"Content-Type": "application/json"})
    unauth_profile = unauth_session.get(f"{BASE_URL}/api/gamification/profile", params={"lang": "ru"}, timeout=30)
    assert unauth_profile.status_code == 401

    isolated_session = requests.Session()
    isolated_session.headers.update({"Content-Type": "application/json"})
    email = f"test_refactor_{uuid.uuid4().hex[:10]}@example.com"
    reg_response = isolated_session.post(
        f"{BASE_URL}/api/auth/register",
        json={"name": "TEST Refactor", "email": email, "password": "admin123"},
        timeout=30,
    )
    assert reg_response.status_code == 200

    auth_profile = isolated_session.get(f"{BASE_URL}/api/gamification/profile", params={"lang": "ru"}, timeout=30)
    assert auth_profile.status_code == 200
    profile_data = auth_profile.json()
    assert isinstance(profile_data.get("totalPoints"), int)

    quiz_response = isolated_session.get(f"{BASE_URL}/api/gamification/daily-quiz", params={"lang": "ru"}, timeout=45)
    assert quiz_response.status_code == 200
    quiz = quiz_response.json()
    selected_option_id = quiz["options"][0]["id"]

    first_answer = isolated_session.post(
        f"{BASE_URL}/api/gamification/daily-quiz/answer",
        json={
            "quizId": quiz["quizId"],
            "selectedOptionId": selected_option_id,
            "language": "ru",
        },
        timeout=45,
    )
    assert first_answer.status_code == 200
    first_payload = first_answer.json()
    assert first_payload["alreadyAnswered"] is False

    duplicate_answer = isolated_session.post(
        f"{BASE_URL}/api/gamification/daily-quiz/answer",
        json={
            "quizId": quiz["quizId"],
            "selectedOptionId": selected_option_id,
            "language": "ru",
        },
        timeout=45,
    )
    assert duplicate_answer.status_code == 200
    duplicate_payload = duplicate_answer.json()
    assert duplicate_payload["alreadyAnswered"] is True
    assert duplicate_payload["pointsAwarded"] == 0