import os
import uuid

import pytest
import requests


# Gamification API regression tests: daily quiz, profile, and answer submission flow
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
def authenticated_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})

    email = f"test_gamification_{uuid.uuid4().hex[:10]}@example.com"
    payload = {
        "name": "TEST Gamification",
        "email": email,
        "password": "admin123",
    }
    response = session.post(f"{BASE_URL}/api/auth/register", json=payload, timeout=20)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data.get("_id"), str)
    assert data.get("email") == email

    return session


def test_daily_quiz_ru_shape_and_no_answer_leak(api_client):
    response = api_client.get(f"{BASE_URL}/api/gamification/daily-quiz", params={"lang": "ru"}, timeout=30)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data.get("quizId"), str) and data["quizId"].startswith("daily-quiz:")
    assert isinstance(data.get("date"), str) and len(data["date"]) == 10
    assert isinstance(data.get("league"), dict)
    assert isinstance(data["league"].get("code"), str) and data["league"]["code"]
    assert isinstance(data["question"], str) and data["question"].strip()
    assert isinstance(data.get("hints"), list) and len(data["hints"]) >= 3
    assert isinstance(data.get("options"), list) and len(data["options"]) == 4
    assert isinstance(data.get("rewardPoints"), int) and data["rewardPoints"] > 0
    assert "correctOptionId" not in data


def test_gamification_profile_requires_auth(api_client):
    response = api_client.get(f"{BASE_URL}/api/gamification/profile", params={"lang": "ru"}, timeout=20)
    assert response.status_code == 401


def test_gamification_profile_shape_authenticated(authenticated_client):
    response = authenticated_client.get(
        f"{BASE_URL}/api/gamification/profile",
        params={"lang": "ru"},
        timeout=20,
    )
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data.get("totalPoints"), int)
    assert isinstance(data.get("quizzesPlayed"), int)
    assert isinstance(data.get("correctAnswers"), int)
    assert isinstance(data.get("currentStreak"), int)
    assert isinstance(data.get("todayAnswered"), bool)
    assert isinstance(data.get("recentAttempts"), list)
    assert isinstance(data.get("badges"), list)


def test_daily_quiz_answer_single_attempt_and_duplicate(authenticated_client):
    quiz_response = authenticated_client.get(
        f"{BASE_URL}/api/gamification/daily-quiz",
        params={"lang": "ru"},
        timeout=30,
    )
    assert quiz_response.status_code == 200
    quiz = quiz_response.json()
    selected_option_id = quiz["options"][0]["id"]

    profile_before_response = authenticated_client.get(
        f"{BASE_URL}/api/gamification/profile",
        params={"lang": "ru"},
        timeout=20,
    )
    assert profile_before_response.status_code == 200
    profile_before = profile_before_response.json()

    first_answer_response = authenticated_client.post(
        f"{BASE_URL}/api/gamification/daily-quiz/answer",
        json={
            "quizId": quiz["quizId"],
            "selectedOptionId": selected_option_id,
            "language": "ru",
        },
        timeout=30,
    )
    assert first_answer_response.status_code == 200
    first_answer = first_answer_response.json()

    assert first_answer["quizId"] == quiz["quizId"]
    assert first_answer["selectedOptionId"] == selected_option_id
    assert isinstance(first_answer.get("correctOptionId"), str) and first_answer["correctOptionId"]
    assert isinstance(first_answer.get("isCorrect"), bool)
    assert isinstance(first_answer.get("pointsAwarded"), int)
    assert first_answer["alreadyAnswered"] is False
    assert isinstance(first_answer.get("profile"), dict)
    assert isinstance(first_answer.get("badges"), list)

    profile_after_first = first_answer["profile"]
    assert profile_after_first["quizzesPlayed"] == profile_before["quizzesPlayed"] + 1

    duplicate_answer_response = authenticated_client.post(
        f"{BASE_URL}/api/gamification/daily-quiz/answer",
        json={
            "quizId": quiz["quizId"],
            "selectedOptionId": selected_option_id,
            "language": "ru",
        },
        timeout=30,
    )
    assert duplicate_answer_response.status_code == 200
    duplicate_answer = duplicate_answer_response.json()

    assert duplicate_answer["quizId"] == quiz["quizId"]
    assert duplicate_answer["selectedOptionId"] == selected_option_id
    assert isinstance(duplicate_answer.get("correctOptionId"), str) and duplicate_answer["correctOptionId"]
    assert duplicate_answer["alreadyAnswered"] is True
    assert duplicate_answer["pointsAwarded"] == 0
    assert isinstance(duplicate_answer.get("profile"), dict)

    profile_after_duplicate = duplicate_answer["profile"]
    assert profile_after_duplicate["quizzesPlayed"] == profile_after_first["quizzesPlayed"]
