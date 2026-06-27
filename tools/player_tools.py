"""
========================================================
Football Scout Agent — Tools Internes
========================================================
Rôle      : Outils de recherche et d'analyse sur la
            base de données locale de joueurs (JSON).
Tools     :
    - search_player   : recherche par nom
    - filter_players  : filtre multi-critères
    - compare_players : comparaison de deux joueurs
    - top_players     : classement par catégorie
========================================================
"""

import json
import os
import re
import unicodedata
from langchain.tools import tool

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/players.json")


def _load_players() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _normalize(text: str) -> str:
    """Minuscule + supprime tous les accents."""
    text = str(text).strip()
    # Enlève guillemets, préfixes "name = ", "name: ", etc.
    text = re.sub(r'^[a-zA-Z_\s]+[:=]\s*', '', text)
    text = text.strip('"\'« » ')
    # Supprime les accents via unicodedata
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def _clean_int(value, default=0):
    try:
        return int(str(value).strip().strip('"\''))
    except:
        return default


def _clean_float(value, default=0.0):
    try:
        return float(str(value).strip().strip('"\''))
    except:
        return default


@tool
def search_player(name: str) -> str:
    """
    Recherche un joueur par son nom et retourne ses statistiques complètes.
    Args:
        name: Le nom du joueur (ex: Mbappe, Haaland, Salah, Bellingham).
    """
    players = _load_players()
    name_norm = _normalize(name)

    matches = [p for p in players if name_norm in _normalize(p["name"])]

    if not matches:
        available = ', '.join(p['name'] for p in players)
        return f"❌ Joueur introuvable. Disponibles : {available}"

    results = []
    for p in matches:
        results.append(
            f"👤 {p['name']} ({p['nationality']}, {p['age']} ans)\n"
            f"🏟️  Club : {p['club']}\n"
            f"⚽  Poste : {p['position']}\n"
            f"📊  Stats : {p['goals_this_season']} buts, {p['assists_this_season']} passes déc. en {p['matches_played']} matchs\n"
            f"⭐  Note : {p['rating']}/10\n"
            f"💶  Valeur : {p['market_value_M']}M€\n"
            f"🦶  Pied : {p['foot']}\n"
            f"🎯  Style : {', '.join(p['style'])}\n"
            f"📝  {p['description']}"
        )
    return "\n\n---\n\n".join(results)


@tool
def filter_players(position: str = "", min_goals: int = 0, min_rating: float = 0.0, max_age: int = 100) -> str:
    """
    Filtre les joueurs selon des critères.
    Args:
        position: Poste (Attaquant, Milieu, Défenseur, Gardien). Vide = tous.
        min_goals: Nombre minimum de buts.
        min_rating: Note minimale sur 10.
        max_age: Âge maximum.
    """
    position = str(position).strip().strip('"\'')
    min_goals = _clean_int(min_goals)
    min_rating = _clean_float(min_rating)
    max_age = _clean_int(max_age, 100)

    players = _load_players()
    filtered = [
        p for p in players
        if (not position or _normalize(position) in _normalize(p["position"]))
        and p["goals_this_season"] >= min_goals
        and p["rating"] >= min_rating
        and p["age"] <= max_age
    ]

    if not filtered:
        return "❌ Aucun joueur ne correspond aux critères."

    filtered.sort(key=lambda x: x["rating"], reverse=True)
    lines = [f"✅ {len(filtered)} joueur(s) :\n"]
    for p in filtered:
        lines.append(
            f"  • {p['name']} ({p['club']}) — {p['position']} — "
            f"{p['goals_this_season']} buts — Note: {p['rating']}/10 — {p['age']} ans"
        )
    return "\n".join(lines)


@tool
def compare_players(player1: str, player2: str) -> str:
    """
    Compare deux joueurs côte à côte sur leurs statistiques clés.
    Args:
        player1: Nom du premier joueur.
        player2: Nom du deuxième joueur.
    """
    players = _load_players()

    def find(name):
        norm = _normalize(name)
        matches = [p for p in players if norm in _normalize(p["name"])]
        return matches[0] if matches else None

    p1 = find(player1)
    p2 = find(player2)

    if not p1:
        return f"❌ Joueur '{player1}' introuvable."
    if not p2:
        return f"❌ Joueur '{player2}' introuvable."

    def w(v1, v2, higher=True):
        if higher:
            return "⬅️" if v1 > v2 else ("➡️" if v2 > v1 else "🟰")
        return "⬅️" if v1 < v2 else ("➡️" if v2 < v1 else "🟰")

    return f"""
🆚 {p1['name']} vs {p2['name']}

{'Critère':<25} {p1['name']:<22} {p2['name']:<22}
{'─'*70}
{'Club':<25} {p1['club']:<22} {p2['club']:<22}
{'Poste':<25} {p1['position']:<22} {p2['position']:<22}
{'Âge':<25} {str(p1['age']):<22} {str(p2['age']):<22}  {w(p1['age'],p2['age'],False)}
{'Buts':<25} {str(p1['goals_this_season']):<22} {str(p2['goals_this_season']):<22}  {w(p1['goals_this_season'],p2['goals_this_season'])}
{'Passes déc.':<25} {str(p1['assists_this_season']):<22} {str(p2['assists_this_season']):<22}  {w(p1['assists_this_season'],p2['assists_this_season'])}
{'Note':<25} {str(p1['rating']):<22} {str(p2['rating']):<22}  {w(p1['rating'],p2['rating'])}
{'Valeur (M€)':<25} {str(p1['market_value_M']):<22} {str(p2['market_value_M']):<22}  {w(p1['market_value_M'],p2['market_value_M'])}

🎯 Style :
  {p1['name']}: {', '.join(p1['style'])}
  {p2['name']}: {', '.join(p2['style'])}

⬅️ = avantage {p1['name']}  |  ➡️ = avantage {p2['name']}  |  🟰 = égalité
"""


@tool
def top_players(category: str = "buts", limit: int = 5) -> str:
    """
    Classement des meilleurs joueurs selon une catégorie.
    Args:
        category: buts | passes | note | valeur
        limit: Nombre de joueurs à afficher (max 10).
    """
    category = str(category).strip().strip('"\'').lower()
    limit = min(_clean_int(limit, 5), 10)
    players = _load_players()

    category_map = {
        "buts": ("goals_this_season", "Buts cette saison"),
        "passes": ("assists_this_season", "Passes décisives"),
        "note": ("rating", "Note globale"),
        "valeur": ("market_value_M", "Valeur marchande (M€)"),
    }

    if category not in category_map:
        category = "buts"

    key, label = category_map[category]
    sorted_players = sorted(players, key=lambda x: x[key], reverse=True)[:limit]

    lines = [f"🏆 TOP {limit} — {label} :\n"]
    for i, p in enumerate(sorted_players, 1):
        lines.append(f"  {i}. {p['name']} ({p['club']}) — {p[key]}")
    return "\n".join(lines)