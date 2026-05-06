from pydantic import BaseModel, Field
from typing import Optional


class RegisterInput(BaseModel):
    name: str
    email: str
    password: str


class LoginInput(BaseModel):
    email: str
    password: str


class FavoriteInput(BaseModel):
    type: str
    item_id: str
    name: str
    crest: str = ""
    league_code: str = ""


class NormalizedArticle(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    imageUrl: Optional[str] = None
    sourceName: Optional[str] = None
    publishedAt: Optional[str] = None
    videoUrl: Optional[str] = None
    provider: Optional[str] = None


class MatchStoryResponse(BaseModel):
    matchId: int
    language: str
    title: str
    summary: str
    keyPoints: list[str]
    whyItMatters: str
    isFallback: bool
    imageUrl: Optional[str] = None
    sources: list[NormalizedArticle] = Field(default_factory=list)
    videoUrl: Optional[str] = None
    generatedAt: str


class QuizOption(BaseModel):
    id: str
    label: str


class DailyQuizResponse(BaseModel):
    quizId: str
    date: str
    league: dict
    question: str
    hints: list[str]
    options: list[QuizOption]
    rewardPoints: int


class DailyCrestQuizResponse(BaseModel):
    quizId: str
    date: str
    league: dict
    question: str
    hints: list[str]
    crestUrl: str
    options: list[QuizOption]
    rewardPoints: int


class QuizAnswerInput(BaseModel):
    quizId: str
    selectedOptionId: str
    language: str = "en"


class BadgeResponse(BaseModel):
    id: str
    title: str
    description: str
    icon: str
    unlocked: bool


class QuizAnswerResponse(BaseModel):
    quizId: str
    selectedOptionId: str
    correctOptionId: str
    isCorrect: bool
    pointsAwarded: int
    alreadyAnswered: bool
    explanation: str
    profile: dict
    badges: list[BadgeResponse]


class GamificationProfileResponse(BaseModel):
    totalPoints: int
    quizzesPlayed: int
    correctAnswers: int
    currentStreak: int
    todayAnswered: bool
    recentAttempts: list[dict]
    badges: list[BadgeResponse]