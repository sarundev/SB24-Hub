"""Real football data from football-data.org (v4), with demo data as a fallback.

Free plan: 10 requests/minute, so every response is cached for a short time.
"""
import time
from datetime import datetime, timedelta, timezone

import httpx

import data

API_URL = "https://api.football-data.org/v4"
CAMBODIA_TZ = timezone(timedelta(hours=7))  # ICT, no daylight saving
COMPETITIONS = ",".join(lg["code"] for lg in data.LEAGUES.values())

# Seconds to reuse a response before asking the API again
TTL_LIVE = 30
TTL_RESULTS = 120
TTL_FIXTURES = 300
TTL_TABLE = 600


class FootballAPIError(Exception):
    pass


def _team(team):
    return team.get("shortName") or team.get("name") or "?"


def _local(utc_date):
    return datetime.fromisoformat(utc_date.replace("Z", "+00:00")).astimezone(CAMBODIA_TZ)


def _score(match):
    full = match["score"]["fullTime"]
    home, away = full.get("home"), full.get("away")
    return f"{home if home is not None else 0} - {away if away is not None else 0}"


def _minute(match):
    if match["status"] == "PAUSED":
        return "HT"
    minute = match.get("minute")
    if not minute:
        return "LIVE"
    extra = match.get("injuryTime")
    return f"{minute}+{extra}'" if extra else f"{minute}'"


def _base(match):
    return {
        "comp": match["competition"]["code"],
        "home": _team(match["homeTeam"]),
        "away": _team(match["awayTeam"]),
    }


class FootballData:
    def __init__(self, api_key):
        self.demo = not api_key
        self._client = None if self.demo else httpx.AsyncClient(
            base_url=API_URL, headers={"X-Auth-Token": api_key}, timeout=15
        )
        self._cache = {}

    async def _get(self, path, params, ttl):
        key = (path, tuple(sorted(params.items())))
        cached = self._cache.get(key)
        if cached and time.monotonic() - cached[0] < ttl:
            return cached[1]

        try:
            resp = await self._client.get(path, params=params)
        except httpx.HTTPError as e:
            if cached:
                return cached[1]
            raise FootballAPIError(f"network error: {e}") from e

        if resp.status_code != 200:
            # Rate limited or temporary problem — older data is better than nothing
            if cached:
                return cached[1]
            raise FootballAPIError(f"HTTP {resp.status_code}: {resp.text[:200]}")

        body = resp.json()
        self._cache[key] = (time.monotonic(), body)
        return body

    async def _matches(self, ttl, **params):
        params["competitions"] = COMPETITIONS
        body = await self._get("/matches", params, ttl)
        return sorted(body.get("matches", []), key=lambda m: m["utcDate"])

    async def live(self):
        if self.demo:
            return data.DEMO_LIVE
        matches = await self._matches(TTL_LIVE, status="IN_PLAY,PAUSED")
        return [{**_base(m), "score": _score(m), "minute": _minute(m)} for m in matches]

    async def results(self, days=3):
        if self.demo:
            return data.DEMO_RESULTS
        today = datetime.now(timezone.utc).date()
        matches = await self._matches(
            TTL_RESULTS,
            status="FINISHED",
            dateFrom=(today - timedelta(days=days)).isoformat(),
            dateTo=today.isoformat(),
        )
        return [
            {**_base(m), "score": _score(m), "date": _local(m["utcDate"]).strftime("%d/%m")}
            for m in reversed(matches)  # newest first
        ]

    async def fixtures(self, days=3):
        if self.demo:
            return data.DEMO_FIXTURES
        today = datetime.now(timezone.utc).date()
        matches = await self._matches(
            TTL_FIXTURES,
            status="SCHEDULED,TIMED",
            dateFrom=today.isoformat(),
            dateTo=(today + timedelta(days=days)).isoformat(),
        )
        return [
            {**_base(m), "time": _local(m["utcDate"]).strftime("%d/%m %H:%M")}
            for m in matches
        ]

    async def table(self, code):
        """Returns [(team, points, played_or_None), ...] ordered by position."""
        if self.demo:
            return [(team, pts, None) for team, pts in data.DEMO_TABLES.get(code, [])]
        body = await self._get(f"/competitions/{code}/standings", {}, TTL_TABLE)
        standings = body.get("standings", [])
        total = next((s for s in standings if s.get("type") == "TOTAL"), None)
        rows = total["table"] if total else []
        return [(_team(r["team"]), r["points"], r["playedGames"]) for r in rows]
