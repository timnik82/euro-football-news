from dotenv import load_dotenv
from pathlib import Path
import logging
import os

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

FOOTBALL_API_KEY = os.environ["FOOTBALL_API_KEY"]
FOOTBALL_API_BASE = "https://api.football-data.org/v4"
COMPETITIONS = "PL,CL,PD,SA,BL1,FL1,PPL"
MATCH_STORY_CACHE_VERSION = "match-story-factual-v3"
JWT_ALGORITHM = "HS256"

LEAGUES = {
    "PL": {"name": "Premier League", "country": "England", "emblem": "https://crests.football-data.org/PL.png"},
    "CL": {"name": "Champions League", "country": "Europe", "emblem": "https://crests.football-data.org/CL.png"},
    "PD": {"name": "La Liga", "country": "Spain", "emblem": "https://crests.football-data.org/laliga.png"},
    "SA": {"name": "Serie A", "country": "Italy", "emblem": "https://crests.football-data.org/c111.png"},
    "BL1": {"name": "Bundesliga", "country": "Germany", "emblem": "https://crests.football-data.org/BL1.png"},
    "FL1": {"name": "Ligue 1", "country": "France", "emblem": "https://crests.football-data.org/FL1.png"},
    "PPL": {"name": "Primeira Liga", "country": "Portugal", "emblem": "https://crests.football-data.org/PPL.png"},
}

LEAGUE_COLORS = {
    "PL": "#7C3AED",
    "CL": "#1E3A5F",
    "PD": "#F97316",
    "SA": "#059669",
    "BL1": "#DC2626",
    "FL1": "#1D4ED8",
    "PPL": "#15803D",
}