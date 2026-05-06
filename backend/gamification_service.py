import hashlib
from datetime import datetime, timezone, timedelta
from config import LEAGUES, logger
from database import db
from football_service import fetch_football_data

QUIZ_LEAGUE_CODES = ["PL", "PD", "SA", "BL1", "FL1", "PPL"]
QUIZ_REWARD_POINTS = 10
FALLBACK_QUIZ_PLAYERS = [
    {
        "player": {"id": 101, "name": "Erling Haaland", "nationality": "Norway"},
        "team": {"name": "Manchester City", "shortName": "Man City", "crest": "https://crests.football-data.org/65.png"},
        "goals": 18,
    },
    {
        "player": {"id": 102, "name": "Kylian Mbappé", "nationality": "France"},
        "team": {"name": "Real Madrid", "shortName": "Real Madrid", "crest": "https://crests.football-data.org/86.png"},
        "goals": 17,
    },
    {
        "player": {"id": 103, "name": "Harry Kane", "nationality": "England"},
        "team": {"name": "FC Bayern München", "shortName": "Bayern", "crest": "https://crests.football-data.org/5.png"},
        "goals": 19,
    },
    {
        "player": {"id": 104, "name": "Robert Lewandowski", "nationality": "Poland"},
        "team": {"name": "FC Barcelona", "shortName": "Barcelona", "crest": "https://crests.football-data.org/81.png"},
        "goals": 16,
    },
]
FALLBACK_QUIZ_TEAMS = [
    {"id": 65, "name": "Manchester City FC", "shortName": "Man City", "crest": "https://crests.football-data.org/65.png"},
    {"id": 86, "name": "Real Madrid CF", "shortName": "Real Madrid", "crest": "https://crests.football-data.org/86.png"},
    {"id": 5, "name": "FC Bayern München", "shortName": "Bayern", "crest": "https://crests.football-data.org/5.png"},
    {"id": 81, "name": "FC Barcelona", "shortName": "Barcelona", "crest": "https://crests.football-data.org/81.png"},
    {"id": 57, "name": "Arsenal FC", "shortName": "Arsenal", "crest": "https://crests.football-data.org/57.png"},
    {"id": 109, "name": "Juventus FC", "shortName": "Juventus", "crest": "https://crests.football-data.org/109.png"},
]

def stable_number(seed: str, modulo: int) -> int:
    if modulo <= 0:
        return 0
    return int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % modulo

def quiz_option_id(name: str) -> str:
    return "player-" + hashlib.sha1(name.encode("utf-8")).hexdigest()[:12]

def team_quiz_option_id(team: dict) -> str:
    raw_id = str(team.get("id") or team.get("name") or team.get("shortName") or "team")
    return "team-" + hashlib.sha1(raw_id.encode("utf-8")).hexdigest()[:12]

def localized_quiz_text(lang: str, key: str, values: dict) -> str:
    language = lang if lang in {"en", "ru", "pt"} else "en"
    templates = {
        "en": {
            "question": "Guess the player: who has scored {goals} goals for {team}?",
            "league": "League: {league}",
            "team": "Club: {team}",
            "nationality": "Nationality: {nationality}",
            "correct": "Correct! It is {player} from {team}. You earned {points} points.",
            "wrong": "Almost! The right answer is {player} from {team}. Try again tomorrow.",
        },
        "ru": {
            "question": "Угадай игрока: кто забил {goals} голов за {team}?",
            "league": "Лига: {league}",
            "team": "Клуб: {team}",
            "nationality": "Гражданство: {nationality}",
            "correct": "Верно! Это {player} из {team}. Ты получил {points} очков.",
            "wrong": "Почти! Правильный ответ — {player} из {team}. Завтра будет новая попытка.",
        },
        "pt": {
            "question": "Adivinha o jogador: quem marcou {goals} golos pelo {team}?",
            "league": "Liga: {league}",
            "team": "Clube: {team}",
            "nationality": "Nacionalidade: {nationality}",
            "correct": "Certo! É {player} do {team}. Ganhaste {points} pontos.",
            "wrong": "Quase! A resposta certa é {player} do {team}. Tenta outra vez amanhã.",
        },
    }
    return templates[language][key].format(**values)

def localized_crest_quiz_text(lang: str, key: str, values: dict) -> str:
    language = lang if lang in {"en", "ru", "pt"} else "en"
    templates = {
        "en": {
            "question": "Which club owns this crest?",
            "league": "League: {league}",
            "hint": "Look closely at the colours and shape",
            "pick": "Pick the club name",
            "correct": "Correct! This crest belongs to {team}. You earned {points} points.",
            "wrong": "Almost! This crest belongs to {team}. Try another crest tomorrow.",
        },
        "ru": {
            "question": "Какому клубу принадлежит эта эмблема?",
            "league": "Лига: {league}",
            "hint": "Посмотри внимательно на цвета и форму",
            "pick": "Выбери название клуба",
            "correct": "Верно! Это эмблема клуба {team}. Ты получил {points} очков.",
            "wrong": "Почти! Это эмблема клуба {team}. Завтра будет новая эмблема.",
        },
        "pt": {
            "question": "A que clube pertence este emblema?",
            "league": "Liga: {league}",
            "hint": "Olha bem para as cores e a forma",
            "pick": "Escolhe o nome do clube",
            "correct": "Certo! Este emblema é do {team}. Ganhaste {points} pontos.",
            "wrong": "Quase! Este emblema é do {team}. Tenta outro emblema amanhã.",
        },
    }
    return templates[language][key].format(**values)

async def get_daily_quiz_data(language: str = "en") -> dict:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    league_code = QUIZ_LEAGUE_CODES[stable_number(today, len(QUIZ_LEAGUE_CODES))]
    league = LEAGUES[league_code]
    scorers = []
    try:
        data = await fetch_football_data(f"/competitions/{league_code}/scorers", cache_minutes=60)
        scorers = data.get("scorers", [])
    except Exception as e:
        logger.info(f"Daily quiz scorer source failed for {league_code}: {e}")
    if len(scorers) < 4:
        scorers = FALLBACK_QUIZ_PLAYERS

    valid_scorers = [s for s in scorers if (s.get("player") or {}).get("name")]
    correct = valid_scorers[stable_number(today + league_code, min(len(valid_scorers), 12))]
    correct_player = correct.get("player") or {}
    correct_team = correct.get("team") or {}
    correct_name = correct_player.get("name")
    correct_option = {"id": quiz_option_id(correct_name), "label": correct_name}
    option_names = [correct_name]
    for scorer in valid_scorers:
        name = (scorer.get("player") or {}).get("name")
        if name and name not in option_names:
            option_names.append(name)
        if len(option_names) == 4:
            break
    while len(option_names) < 4:
        for fallback in FALLBACK_QUIZ_PLAYERS:
            name = fallback["player"]["name"]
            if name not in option_names:
                option_names.append(name)
            if len(option_names) == 4:
                break
    options = [{"id": quiz_option_id(name), "label": name} for name in option_names[:4]]
    options.sort(key=lambda option: stable_number(today + option["id"], 1000000))

    values = {
        "goals": correct.get("goals") or 0,
        "team": correct_team.get("shortName") or correct_team.get("name") or "Team",
        "league": league["name"],
        "nationality": correct_player.get("nationality") or "?",
        "player": correct_name,
        "points": QUIZ_REWARD_POINTS,
    }
    return {
        "quizId": f"daily-quiz:{today}:{league_code}",
        "date": today,
        "league": {"code": league_code, "name": league["name"], "emblem": league.get("emblem", "")},
        "question": localized_quiz_text(language, "question", values),
        "hints": [
            localized_quiz_text(language, "league", values),
            localized_quiz_text(language, "team", values),
            localized_quiz_text(language, "nationality", values),
        ],
        "options": options,
        "rewardPoints": QUIZ_REWARD_POINTS,
        "correctOptionId": correct_option["id"],
        "correctPlayer": correct_name,
        "correctTeam": values["team"],
    }

async def get_daily_crest_quiz_data(language: str = "en") -> dict:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    league_code = QUIZ_LEAGUE_CODES[stable_number(today + "crest", len(QUIZ_LEAGUE_CODES))]
    league = LEAGUES[league_code]
    teams = []
    try:
        data = await fetch_football_data(f"/competitions/{league_code}/standings", cache_minutes=60)
        for standing in data.get("standings", []):
            if standing.get("type") == "TOTAL" or not teams:
                teams = [row.get("team") or {} for row in standing.get("table", [])]
                if teams:
                    break
    except Exception as e:
        logger.info(f"Daily crest quiz standings source failed for {league_code}: {e}")
    valid_teams = [team for team in teams if team.get("crest") and (team.get("shortName") or team.get("name"))]
    if len(valid_teams) < 4:
        valid_teams = FALLBACK_QUIZ_TEAMS

    correct = valid_teams[stable_number(today + league_code + "crest", min(len(valid_teams), 12))]
    correct_name = correct.get("shortName") or correct.get("name")
    option_teams = [correct]
    seen_names = {correct_name}
    for team in valid_teams:
        name = team.get("shortName") or team.get("name")
        if name and name not in seen_names:
            option_teams.append(team)
            seen_names.add(name)
        if len(option_teams) == 4:
            break
    while len(option_teams) < 4:
        for fallback in FALLBACK_QUIZ_TEAMS:
            name = fallback.get("shortName") or fallback.get("name")
            if name not in seen_names:
                option_teams.append(fallback)
                seen_names.add(name)
            if len(option_teams) == 4:
                break
    options = [
        {"id": team_quiz_option_id(team), "label": team.get("shortName") or team.get("name")}
        for team in option_teams[:4]
    ]
    options.sort(key=lambda option: stable_number(today + option["id"], 1000000))
    values = {
        "league": league["name"],
        "team": correct_name,
        "points": QUIZ_REWARD_POINTS,
    }
    return {
        "quizId": f"crest-quiz:{today}:{league_code}",
        "date": today,
        "league": {"code": league_code, "name": league["name"], "emblem": league.get("emblem", "")},
        "question": localized_crest_quiz_text(language, "question", values),
        "hints": [
            localized_crest_quiz_text(language, "league", values),
            localized_crest_quiz_text(language, "hint", values),
            localized_crest_quiz_text(language, "pick", values),
        ],
        "crestUrl": correct.get("crest"),
        "options": options,
        "rewardPoints": QUIZ_REWARD_POINTS,
        "correctOptionId": team_quiz_option_id(correct),
        "correctTeam": correct_name,
    }

def calculate_quiz_streak(attempts: list[dict]) -> int:
    answered_dates = sorted({(attempt.get("quizId", "").split(":") + [""])[1] for attempt in attempts if attempt.get("quizId")}, reverse=True)
    if not answered_dates:
        return 0
    streak = 0
    cursor = datetime.now(timezone.utc).date()
    answered_set = set(answered_dates)
    while cursor.isoformat() in answered_set:
        streak += 1
        cursor = cursor - timedelta(days=1)
    return streak

def build_badges(profile: dict, language: str = "en") -> list[dict]:
    lang = language if language in {"en", "ru", "pt"} else "en"
    labels = {
        "en": {
            "first": ("First Kick", "Answer your first daily quiz"),
            "sharp": ("Sharp Shooter", "Get 3 answers right"),
            "streak": ("Three-Day Streak", "Play 3 days in a row"),
            "legend": ("Mini Legend", "Collect 50 points"),
        },
        "ru": {
            "first": ("Первый удар", "Ответь на первую ежедневную викторину"),
            "sharp": ("Меткий удар", "Ответь правильно 3 раза"),
            "streak": ("Серия 3 дня", "Играй 3 дня подряд"),
            "legend": ("Мини-легенда", "Собери 50 очков"),
        },
        "pt": {
            "first": ("Primeiro Remate", "Responde ao primeiro quiz diário"),
            "sharp": ("Pontaria Certa", "Acerta 3 respostas"),
            "streak": ("Sequência de 3 Dias", "Joga 3 dias seguidos"),
            "legend": ("Mini Lenda", "Junta 50 pontos"),
        },
    }
    badge_defs = [
        ("first-kick", "first", "⚽", profile["quizzesPlayed"] >= 1),
        ("sharp-shooter", "sharp", "🎯", profile["correctAnswers"] >= 3),
        ("three-day-streak", "streak", "🔥", profile["currentStreak"] >= 3),
        ("mini-legend", "legend", "🏆", profile["totalPoints"] >= 50),
    ]
    badges = []
    for badge_id, label_key, icon, unlocked in badge_defs:
        title, description = labels[lang][label_key]
        badges.append({"id": badge_id, "title": title, "description": description, "icon": icon, "unlocked": unlocked})
    return badges

async def build_gamification_profile(user_id: str, language: str = "en") -> dict:
    attempts = await db.quiz_attempts.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("answeredAt", -1).to_list(365)
    total_points = sum(int(attempt.get("pointsAwarded", 0)) for attempt in attempts)
    correct_answers = sum(1 for attempt in attempts if attempt.get("isCorrect"))
    current_streak = calculate_quiz_streak(attempts)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    profile = {
        "totalPoints": total_points,
        "quizzesPlayed": len(attempts),
        "correctAnswers": correct_answers,
        "currentStreak": current_streak,
        "todayAnswered": any((attempt.get("quizId", "").split(":") + [""])[1] == today for attempt in attempts),
        "recentAttempts": attempts[:7],
    }
    profile["badges"] = build_badges(profile, language)
    return profile
