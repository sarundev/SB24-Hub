NEWS_URL = "https://www.bbc.com/sport/football"

# key -> football-data.org competition code (all included in the free plan)
LEAGUES = {
    "epl": {"name": "🏴 Premier League", "code": "PL"},
    "laliga": {"name": "🇪🇸 La Liga", "code": "PD"},
    "seriea": {"name": "🇮🇹 Serie A", "code": "SA"},
    "bundesliga": {"name": "🇩🇪 Bundesliga", "code": "BL1"},
    "ligue1": {"name": "🇫🇷 Ligue 1", "code": "FL1"},
    "ucl": {"name": "🇪🇺 Champions League", "code": "CL"},
}

COMPETITION_NAMES = {lg["code"]: lg["name"] for lg in LEAGUES.values()}


# ---------- ទិន្នន័យគំរូ (Demo) — ប្រើតែពេលមិនទាន់មាន FOOTBALL_DATA_KEY ----------

DEMO_LIVE = [
    {"comp": "PL", "home": "Man United", "away": "Chelsea", "score": "1 - 0", "minute": "67'"},
    {"comp": "PD", "home": "Barcelona", "away": "Real Madrid", "score": "2 - 1", "minute": "78'"},
]

DEMO_RESULTS = [
    {"comp": "PL", "home": "Liverpool", "away": "Arsenal", "score": "2 - 1", "date": "08/10"},
    {"comp": "PD", "home": "Barcelona", "away": "Sevilla", "score": "3 - 0", "date": "08/10"},
    {"comp": "FL1", "home": "PSG", "away": "Lyon", "score": "2 - 2", "date": "08/10"},
]

DEMO_FIXTURES = [
    {"comp": "PD", "home": "Real Madrid", "away": "Barcelona", "time": "09/10 02:00"},
    {"comp": "PL", "home": "Arsenal", "away": "Chelsea", "time": "09/10 04:30"},
]

DEMO_TABLES = {
    "PL": [("Arsenal", 25), ("Liverpool", 23), ("Chelsea", 21), ("Man City", 20), ("Tottenham", 18)],
    "PD": [("Real Madrid", 24), ("Barcelona", 22), ("Atleti", 19), ("Villarreal", 17), ("Real Betis", 15)],
    "SA": [("Inter", 23), ("Napoli", 22), ("Juventus", 20), ("Milan", 19), ("Roma", 16)],
    "BL1": [("Bayern", 25), ("Leverkusen", 21), ("Dortmund", 20), ("Leipzig", 18), ("Stuttgart", 16)],
    "FL1": [("PSG", 24), ("Monaco", 20), ("Marseille", 19), ("Lille", 17), ("Lyon", 15)],
    "CL": [("Real Madrid", 9), ("Bayern", 9), ("Arsenal", 7), ("Inter", 7), ("PSG", 6)],
}
