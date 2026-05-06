from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request
from auth_service import get_current_user
from database import db
from gamification_service import (
    QUIZ_REWARD_POINTS,
    build_gamification_profile,
    get_daily_crest_quiz_data,
    get_daily_quiz_data,
    localized_crest_quiz_text,
    localized_quiz_text,
)
from schemas import DailyCrestQuizResponse, DailyQuizResponse, GamificationProfileResponse, QuizAnswerInput, QuizAnswerResponse

router = APIRouter(tags=["gamification"])

@router.get("/gamification/daily-quiz", response_model=DailyQuizResponse)
async def get_daily_quiz(lang: str = "en"):
    quiz = await get_daily_quiz_data(lang)
    return {
        "quizId": quiz["quizId"],
        "date": quiz["date"],
        "league": quiz["league"],
        "question": quiz["question"],
        "hints": quiz["hints"],
        "options": quiz["options"],
        "rewardPoints": quiz["rewardPoints"],
    }

@router.get("/gamification/crest-quiz", response_model=DailyCrestQuizResponse)
async def get_daily_crest_quiz(lang: str = "en"):
    quiz = await get_daily_crest_quiz_data(lang)
    return {
        "quizId": quiz["quizId"],
        "date": quiz["date"],
        "league": quiz["league"],
        "question": quiz["question"],
        "hints": quiz["hints"],
        "crestUrl": quiz["crestUrl"],
        "options": quiz["options"],
        "rewardPoints": quiz["rewardPoints"],
    }

@router.get("/gamification/profile", response_model=GamificationProfileResponse)
async def get_gamification_profile(request: Request, lang: str = "en"):
    user = await get_current_user(request)
    return await build_gamification_profile(user["_id"], lang)

@router.post("/gamification/daily-quiz/answer", response_model=QuizAnswerResponse)
async def answer_daily_quiz(data: QuizAnswerInput, request: Request):
    user = await get_current_user(request)
    quiz = await get_daily_quiz_data(data.language)
    if data.quizId != quiz["quizId"]:
        raise HTTPException(400, "Quiz is no longer active")

    existing = await db.quiz_attempts.find_one(
        {"user_id": user["_id"], "quizId": data.quizId},
        {"_id": 0}
    )
    if existing:
        profile = await build_gamification_profile(user["_id"], data.language)
        explanation_key = "correct" if existing.get("isCorrect") else "wrong"
        explanation = localized_quiz_text(data.language, explanation_key, {
            "player": quiz["correctPlayer"],
            "team": quiz["correctTeam"],
            "points": existing.get("pointsAwarded", 0),
            "goals": 0,
            "league": quiz["league"]["name"],
            "nationality": "",
        })
        return {
            "quizId": data.quizId,
            "selectedOptionId": existing["selectedOptionId"],
            "correctOptionId": existing["correctOptionId"],
            "isCorrect": existing["isCorrect"],
            "pointsAwarded": 0,
            "alreadyAnswered": True,
            "explanation": explanation,
            "profile": profile,
            "badges": profile["badges"],
        }

    is_correct = data.selectedOptionId == quiz["correctOptionId"]
    points_awarded = QUIZ_REWARD_POINTS if is_correct else 2
    attempt_doc = {
        "user_id": user["_id"],
        "quizId": data.quizId,
        "selectedOptionId": data.selectedOptionId,
        "correctOptionId": quiz["correctOptionId"],
        "isCorrect": is_correct,
        "pointsAwarded": points_awarded,
        "answeredAt": datetime.now(timezone.utc).isoformat(),
    }
    await db.quiz_attempts.insert_one(attempt_doc)
    profile = await build_gamification_profile(user["_id"], data.language)
    explanation_key = "correct" if is_correct else "wrong"
    explanation = localized_quiz_text(data.language, explanation_key, {
        "player": quiz["correctPlayer"],
        "team": quiz["correctTeam"],
        "points": points_awarded,
        "goals": 0,
        "league": quiz["league"]["name"],
        "nationality": "",
    })
    return {
        "quizId": data.quizId,
        "selectedOptionId": data.selectedOptionId,
        "correctOptionId": quiz["correctOptionId"],
        "isCorrect": is_correct,
        "pointsAwarded": points_awarded,
        "alreadyAnswered": False,
        "explanation": explanation,
        "profile": profile,
        "badges": profile["badges"],
    }

@router.post("/gamification/crest-quiz/answer", response_model=QuizAnswerResponse)
async def answer_daily_crest_quiz(data: QuizAnswerInput, request: Request):
    user = await get_current_user(request)
    quiz = await get_daily_crest_quiz_data(data.language)
    if data.quizId != quiz["quizId"]:
        raise HTTPException(400, "Quiz is no longer active")

    existing = await db.quiz_attempts.find_one(
        {"user_id": user["_id"], "quizId": data.quizId},
        {"_id": 0}
    )
    if existing:
        profile = await build_gamification_profile(user["_id"], data.language)
        explanation_key = "correct" if existing.get("isCorrect") else "wrong"
        explanation = localized_crest_quiz_text(data.language, explanation_key, {
            "team": quiz["correctTeam"],
            "league": quiz["league"]["name"],
            "points": existing.get("pointsAwarded", 0),
        })
        return {
            "quizId": data.quizId,
            "selectedOptionId": existing["selectedOptionId"],
            "correctOptionId": existing["correctOptionId"],
            "isCorrect": existing["isCorrect"],
            "pointsAwarded": 0,
            "alreadyAnswered": True,
            "explanation": explanation,
            "profile": profile,
            "badges": profile["badges"],
        }

    is_correct = data.selectedOptionId == quiz["correctOptionId"]
    points_awarded = QUIZ_REWARD_POINTS if is_correct else 2
    attempt_doc = {
        "user_id": user["_id"],
        "quizId": data.quizId,
        "selectedOptionId": data.selectedOptionId,
        "correctOptionId": quiz["correctOptionId"],
        "isCorrect": is_correct,
        "pointsAwarded": points_awarded,
        "answeredAt": datetime.now(timezone.utc).isoformat(),
    }
    await db.quiz_attempts.insert_one(attempt_doc)
    profile = await build_gamification_profile(user["_id"], data.language)
    explanation_key = "correct" if is_correct else "wrong"
    explanation = localized_crest_quiz_text(data.language, explanation_key, {
        "team": quiz["correctTeam"],
        "league": quiz["league"]["name"],
        "points": points_awarded,
    })
    return {
        "quizId": data.quizId,
        "selectedOptionId": data.selectedOptionId,
        "correctOptionId": quiz["correctOptionId"],
        "isCorrect": is_correct,
        "pointsAwarded": points_awarded,
        "alreadyAnswered": False,
        "explanation": explanation,
        "profile": profile,
        "badges": profile["badges"],
    }
