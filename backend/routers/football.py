from fastapi import APIRouter
from routers.leagues import router as leagues_router
from routers.teams import router as teams_router
from routers.matches import router as matches_router
from routers.stories import router as stories_router
from routers.search import router as search_router

router = APIRouter(tags=["football"])
router.include_router(leagues_router)
router.include_router(teams_router)
router.include_router(matches_router)
router.include_router(stories_router)
router.include_router(search_router)
