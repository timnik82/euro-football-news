import os
from motor.motor_asyncio import AsyncIOMotorClient
from config import ROOT_DIR, load_dotenv

load_dotenv(ROOT_DIR / ".env")

mongo_client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = mongo_client[os.environ["DB_NAME"]]