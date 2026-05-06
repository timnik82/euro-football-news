from datetime import datetime, timezone
from fastapi import APIRouter, Request
from auth_service import get_current_user
from database import db
from schemas import FavoriteInput

router = APIRouter(tags=["favorites"])

# ============ FAVORITES ============
@router.get("/favorites")
async def get_favorites(request: Request):
    user = await get_current_user(request)
    favs = await db.favorites.find({"user_id": user["_id"]}, {"_id": 0}).to_list(100)
    return favs

@router.post("/favorites")
async def toggle_favorite(data: FavoriteInput, request: Request):
    user = await get_current_user(request)
    existing = await db.favorites.find_one({
        "user_id": user["_id"], "type": data.type, "item_id": data.item_id
    })
    if existing:
        await db.favorites.delete_one({"_id": existing["_id"]})
        return {"action": "removed", "type": data.type, "item_id": data.item_id}
    fav_doc = {
        "user_id": user["_id"], "type": data.type, "item_id": data.item_id,
        "name": data.name, "crest": data.crest, "league_code": data.league_code,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.favorites.insert_one(fav_doc)
    return {"action": "added", "type": data.type, "item_id": data.item_id, "name": data.name}
