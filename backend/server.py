from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

import os
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from auth_service import seed_admin, write_test_credentials_file
from database import db, mongo_client
from routers.auth import router as auth_router
from routers.favorites import router as favorites_router
from routers.football import router as football_router
from routers.gamification import router as gamification_router

app = FastAPI()


def configured_cors_origins() -> list[str]:
    return [origin.strip() for origin in os.environ["CORS_ORIGINS"].split(",") if origin.strip()]

app.include_router(auth_router, prefix="/api")
app.include_router(football_router, prefix="/api")
app.include_router(gamification_router, prefix="/api")
app.include_router(favorites_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.api_cache.create_index("key", unique=True)
    await db.api_cache.create_index("expires_at", expireAfterSeconds=0)
    await db.favorites.create_index([("user_id", 1), ("type", 1), ("item_id", 1)], unique=True)
    await db.match_stories.create_index([("matchId", 1), ("language", 1)], unique=True)
    await db.quiz_attempts.create_index([("user_id", 1), ("quizId", 1)], unique=True)
    await db.login_attempts.create_index("identifier", unique=True)
    await db.login_attempts.create_index("locked_until")
    await seed_admin()
    write_test_credentials_file()


@app.on_event("shutdown")
async def shutdown():
    mongo_client.close()
