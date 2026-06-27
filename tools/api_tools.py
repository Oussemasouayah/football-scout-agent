"""
Tool externe : API Football (api-football.com)
"""

import os
import requests
from langchain.tools import tool

API_BASE_URL = "https://v3.football.api-sports.io"


def _get_headers():
    api_key = os.getenv("API_FOOTBALL_KEY", "")
    if not api_key:
        return None
    return {
        "x-rapidapi-host": "v3.football.api-sports.io",
        "x-rapidapi-key": api_key,
    }


def _safe_response_list(r) -> list:
    """Parse la réponse API en gérant tous les cas foireux (None, erreurs, quota dépassé)."""
    try:
        data = r.json()
    except Exception:
        return []
    if not isinstance(data, dict):
        return []
    # L'API Football renvoie parfois des erreurs dans 'errors' (quota, plan gratuit limité, etc.)
    errors = data.get("errors")
    if errors:
        raise RuntimeError(str(errors))
    response = data.get("response")
    if not isinstance(response, list):
        return []
    return response


@tool
def get_live_matches() -> str:
    """Récupère les matchs de football en direct en ce moment. Aucun paramètre requis."""
    headers = _get_headers()
    if not headers:
        return "⚠️ API_FOOTBALL_KEY non configurée dans .env — données live indisponibles."
    try:
        r = requests.get(f"{API_BASE_URL}/fixtures", params={"live": "all"}, headers=headers, timeout=10)
        fixtures = _safe_response_list(r)
        if not fixtures:
            return "⚽ Aucun match en direct pour le moment (ou plan API gratuit ne donnant pas accès au live)."
        lines = [f"🔴 {len(fixtures)} match(s) en direct :\n"]
        for f in fixtures[:10]:
            home = f.get("teams", {}).get("home", {}).get("name", "?")
            away = f.get("teams", {}).get("away", {}).get("name", "?")
            sh = f.get("goals", {}).get("home") or 0
            sa = f.get("goals", {}).get("away") or 0
            minute = f.get("fixture", {}).get("status", {}).get("elapsed", "?")
            league = f.get("league", {}).get("name", "?")
            lines.append(f"  ⚽ {home} {sh} - {sa} {away}  ({minute}') — {league}")
        return "\n".join(lines)
    except RuntimeError as e:
        return f"⚠️ L'API Football a renvoyé une erreur (probablement quota gratuit dépassé ou endpoint non inclus dans le plan) : {str(e)}"
    except Exception as e:
        return f"❌ Erreur technique : {str(e)}"


@tool
def get_league_standings(league_id: int = 39, season: int = 2024) -> str:
    """
    Récupère le classement d'une ligue.
    Args:
        league_id: 39=Premier League, 140=La Liga, 61=Ligue 1, 135=Serie A, 78=Bundesliga
        season: Année de début de saison (ex: 2024 pour 2024/2025)
    """
    headers = _get_headers()
    if not headers:
        return "⚠️ API_FOOTBALL_KEY non configurée dans .env — classements indisponibles."

    league_names = {
        39: "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿", 140: "La Liga 🇪🇸",
        61: "Ligue 1 🇫🇷", 135: "Serie A 🇮🇹",
        78: "Bundesliga 🇩🇪", 2: "Champions League 🏆",
    }

    try:
        league_id = int(league_id)
        season = int(season)
        r = requests.get(
            f"{API_BASE_URL}/standings",
            params={"league": league_id, "season": season},
            headers=headers, timeout=10
        )
        data = _safe_response_list(r)
        if not data:
            return f"❌ Classement introuvable (ligue {league_id}, saison {season}). Vérifie le quota de ta clé API."

        league_name = league_names.get(league_id, f"Ligue {league_id}")
        standings = data[0]["league"]["standings"][0]

        lines = [f"📊 CLASSEMENT — {league_name} (Saison {season}/{season+1}) :\n"]
        lines.append(f"  {'Pos':<4} {'Équipe':<25} {'Pts':<5} {'J':<4} {'V':<4} {'N':<4} {'D':<4} {'Diff'}")
        lines.append("  " + "─" * 54)
        for t in standings[:10]:
            diff = t["goalsDiff"]
            diff_str = f"+{diff}" if diff > 0 else str(diff)
            lines.append(
                f"  {t['rank']:<4} {t['team']['name']:<25} {t['points']:<5} "
                f"{t['all']['played']:<4} {t['all']['win']:<4} {t['all']['draw']:<4} "
                f"{t['all']['lose']:<4} {diff_str}"
            )
        return "\n".join(lines)
    except RuntimeError as e:
        return f"⚠️ Erreur API (quota/plan) : {str(e)}"
    except Exception as e:
        return f"❌ Erreur technique : {str(e)}"


@tool
def get_recent_matches(team_name: str, last_n: int = 5) -> str:
    """
    Récupère les derniers matchs joués d'une équipe.
    Args:
        team_name: Nom de l'équipe en anglais (ex: Liverpool, Real Madrid, Barcelona)
        last_n: Nombre de matchs à récupérer (max 10)
    """
    headers = _get_headers()
    if not headers:
        return "⚠️ API_FOOTBALL_KEY non configurée dans .env — matchs récents indisponibles."
    try:
        last_n = min(int(last_n), 10)

        sr = requests.get(f"{API_BASE_URL}/teams", params={"search": team_name}, headers=headers, timeout=10)
        teams = _safe_response_list(sr)
        if not teams:
            return f"❌ Équipe '{team_name}' introuvable (vérifie l'orthographe en anglais, ou quota API dépassé)."

        team = teams[0]["team"]
        team_id = team["id"]

        fr = requests.get(
            f"{API_BASE_URL}/fixtures",
            params={"team": team_id, "last": last_n},
            headers=headers, timeout=10
        )
        fixtures = _safe_response_list(fr)

        if not fixtures:
            return f"❌ Aucun match récent trouvé pour {team['name']} (saison probablement terminée ou quota API dépassé)."

        lines = [f"📅 DERNIERS MATCHS — {team['name']} :\n"]
        for f in reversed(fixtures):
            date = f["fixture"]["date"][:10]
            home = f["teams"]["home"]["name"]
            away = f["teams"]["away"]["name"]
            sh = f["goals"]["home"]
            sa = f["goals"]["away"]
            league = f["league"]["name"]
            is_home = home == team["name"]
            if sh == sa:
                result = "🟡 NUL"
            elif (is_home and sh and sh > (sa or 0)) or (not is_home and sa and sa > (sh or 0)):
                result = "🟢 VICTOIRE"
            else:
                result = "🔴 DÉFAITE"
            lines.append(f"  {result} | {date} | {home} {sh}-{sa} {away} ({league})")
        return "\n".join(lines)
    except RuntimeError as e:
        return f"⚠️ Erreur API (quota/plan) : {str(e)}"
    except Exception as e:
        return f"❌ Erreur technique : {str(e)}"