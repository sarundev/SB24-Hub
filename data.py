# ទិន្នន័យគំរូ (Demo) — អាចប្តូរទៅទាញពី Football API ពេលក្រោយ

LIVE_MATCHES = [
    {"home": "Manchester United", "away": "Chelsea", "score": "1 - 0", "minute": "67'"},
    {"home": "Barcelona", "away": "Real Madrid", "score": "2 - 1", "minute": "78'"},
]

RESULTS = [
    {"home": "Liverpool", "away": "Arsenal", "score": "2 - 1"},
    {"home": "Barcelona", "away": "Sevilla", "score": "3 - 0"},
    {"home": "PSG", "away": "Lyon", "score": "2 - 2"},
]

FIXTURES = [
    {"home": "Real Madrid", "away": "Barcelona", "time": "02:00 AM"},
    {"home": "Arsenal", "away": "Chelsea", "time": "04:30 AM"},
]

NEWS_URL = "https://www.bbc.com/sport/football"

LEAGUES = {
    "epl": {
        "name": "🏴 Premier League",
        "table": [("Arsenal", 25), ("Liverpool", 23), ("Chelsea", 21), ("Man City", 20), ("Tottenham", 18)],
    },
    "laliga": {
        "name": "🇪🇸 La Liga",
        "table": [("Real Madrid", 24), ("Barcelona", 22), ("Atletico Madrid", 19), ("Villarreal", 17), ("Real Betis", 15)],
    },
    "seriea": {
        "name": "🇮🇹 Serie A",
        "table": [("Inter", 23), ("Napoli", 22), ("Juventus", 20), ("AC Milan", 19), ("Roma", 16)],
    },
    "bundesliga": {
        "name": "🇩🇪 Bundesliga",
        "table": [("Bayern Munich", 25), ("Leverkusen", 21), ("Dortmund", 20), ("Leipzig", 18), ("Stuttgart", 16)],
    },
    "ligue1": {
        "name": "🇫🇷 Ligue 1",
        "table": [("PSG", 24), ("Monaco", 20), ("Marseille", 19), ("Lille", 17), ("Lyon", 15)],
    },
    "ucl": {
        "name": "🇪🇺 Champions League",
        "table": [("Real Madrid", 9), ("Bayern Munich", 9), ("Arsenal", 7), ("Inter", 7), ("PSG", 6)],
    },
}
