"""
DataPace Data Loader (SQLite)
==============================
Remplace la lecture des fichiers Excel par des requetes SQLite.
Retourne exactement les memes formats que les anciennes fonctions
load_finishers(), load_biggest(), load_marathon(), load_semi(),
load_winners(), load_sporthive_avg(), build_times_db() de generate_dashboard.py
afin de garantir la compatibilite avec le rendu HTML/JS existant.
"""
import sqlite3
from pathlib import Path
from typing import Optional

from .config import DB_FILE, ASO_KEYWORDS, WMM_KEYWORDS


def _connect(db_path: Optional[Path] = None):
    path = db_path or DB_FILE
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def _detect_badge(name: str) -> str:
    low = name.lower()
    if any(k in low for k in WMM_KEYWORDS):
        return "WMM"
    if any(k in low for k in ASO_KEYWORDS):
        return "ASO"
    return "Autre"


# ── Distance mapping (DB distance → JS distance key) ────────────────────────
_DIST_MAP_WINNERS = {"MARATHON": "42K", "SEMI": "21K", "10KM": "10K", "AUTRE": "AUTRE"}


def load_finishers(db_path: Optional[Path] = None) -> list:
    """
    Retourne la liste au format attendu par le JS du dashboard :
    [{"p": period, "c": city, "d": distance, "r": race_name,
      "y3": count_2023, "y4": count_2024, "y5": count_2025, "y6": count_2026,
      "hist": {year: count, ...}, "fy": first_edition_year_or_None}, ...]
    """
    conn = _connect(db_path)
    try:
        events = conn.execute(
            "SELECT id, name, city, distance, period, first_edition FROM events ORDER BY period, name"
        ).fetchall()

        rows = []
        for ev in events:
            # Chercher tous les finishers de cet evenement
            fins = conn.execute(
                "SELECT year, count FROM finishers WHERE event_id = ? ORDER BY year",
                (ev["id"],)
            ).fetchall()

            if not fins:
                continue

            hist = {}
            for f in fins:
                yr, cnt = f["year"], f["count"]
                if cnt is not None:
                    hist[yr] = cnt

            if not hist:
                continue

            # Determiner la premiere edition (premiere annee avec count != x/-3)
            # Dans la BDD, les annees "x" ne sont pas stockees, donc la premiere
            # annee presente est la premiere edition
            sorted_years = sorted(hist.keys())
            first_yr = None
            if sorted_years:
                candidate = sorted_years[0]
                # Seul afficher l'etoile si >= 2000
                if candidate >= 2000:
                    first_yr = candidate

            # Raccourcis pour les 4 dernieres annees
            def get_yr(y):
                return hist.get(y)

            rows.append({
                "p": ev["period"] or "",
                "c": ev["city"] or "",
                "d": ev["distance"],
                "r": ev["name"],
                "y3": get_yr(2023),
                "y4": get_yr(2024),
                "y5": get_yr(2025),
                "y6": get_yr(2026),
                "hist": hist,
                "fy": first_yr,
            })

        print(f"  Finishers  : {len(rows)} courses")
        return rows
    finally:
        conn.close()


def load_biggest(db_path: Optional[Path] = None) -> list:
    """
    Retourne le top des evenements au format :
    [{"c": city, "r": race, "y3".."y6": count, "hist": {year: count}}, ...]

    Prend les evenements qui ont des finishers recents, tries par taille.
    """
    conn = _connect(db_path)
    try:
        # Evenements avec le plus de finishers sur les annees recentes
        query = """
            SELECT e.id, e.name, e.city, e.distance,
                   MAX(CASE WHEN f.year = 2023 THEN f.count END) as y3,
                   MAX(CASE WHEN f.year = 2024 THEN f.count END) as y4,
                   MAX(CASE WHEN f.year = 2025 THEN f.count END) as y5,
                   MAX(CASE WHEN f.year = 2026 THEN f.count END) as y6,
                   MAX(f.count) as peak
            FROM events e
            JOIN finishers f ON e.id = f.event_id AND f.count > 0
            GROUP BY e.id
            ORDER BY peak DESC
            LIMIT 50
        """
        events = conn.execute(query).fetchall()

        rows = []
        for ev in events:
            fins = conn.execute(
                "SELECT year, count FROM finishers WHERE event_id = ? AND count > 0 ORDER BY year",
                (ev["id"],)
            ).fetchall()
            hist = {f["year"]: f["count"] for f in fins}

            rows.append({
                "c": ev["city"] or "",
                "r": ev["name"],
                "y3": ev["y3"],
                "y4": ev["y4"],
                "y5": ev["y5"],
                "y6": ev["y6"],
                "hist": hist,
            })

        print(f"  Biggest    : {len(rows)} courses")
        return rows
    finally:
        conn.close()


def load_marathon(year: int, db_path: Optional[Path] = None) -> list:
    """
    Retourne les temps moyens marathon au format :
    [{"race": name, "city": city, "finishers": n, "avg": "HH:MM:SS",
      "men": "HH:MM:SS", "women": "HH:MM:SS", "year": year}, ...]
    """
    conn = _connect(db_path)
    try:
        query = """
            SELECT e.name, e.city,
                   a.avg_time, a.men_time, a.women_time,
                   f.count as finishers
            FROM avg_times a
            JOIN events e ON a.event_id = e.id
            LEFT JOIN finishers f ON f.event_id = e.id AND f.year = a.year
            WHERE a.year = ? AND e.distance = 'MARATHON'
            ORDER BY e.name
        """
        results = conn.execute(query, (year,)).fetchall()
        rows = []
        for r in results:
            if r["avg_time"] or r["men_time"] or r["women_time"]:
                rows.append({
                    "race": r["name"],
                    "city": r["city"] or "",
                    "finishers": r["finishers"],
                    "avg": r["avg_time"],
                    "men": r["men_time"],
                    "women": r["women_time"],
                    "year": year,
                })
        print(f"  Marathon {year}: {len(rows)} courses")
        return rows
    finally:
        conn.close()


def load_semi(db_path: Optional[Path] = None) -> dict:
    """
    Retourne les temps moyens semi par annee au format :
    {year: [{"race": name, "city": city, "finishers": n, "avg": "HH:MM:SS",
             "men": ..., "women": ..., "year": year}, ...], ...}
    """
    conn = _connect(db_path)
    try:
        query = """
            SELECT a.year, e.name, e.city,
                   a.avg_time, a.men_time, a.women_time,
                   f.count as finishers
            FROM avg_times a
            JOIN events e ON a.event_id = e.id
            LEFT JOIN finishers f ON f.event_id = e.id AND f.year = a.year
            WHERE e.distance = 'SEMI'
            ORDER BY a.year, e.name
        """
        results = conn.execute(query).fetchall()
        all_data = {}
        for r in results:
            if not (r["avg_time"] or r["men_time"] or r["women_time"]):
                continue
            yr = r["year"]
            if yr not in all_data:
                all_data[yr] = []
            all_data[yr].append({
                "race": r["name"],
                "city": r["city"] or "",
                "finishers": r["finishers"],
                "avg": r["avg_time"],
                "men": r["men_time"],
                "women": r["women_time"],
                "year": yr,
            })
        for yr, rows in sorted(all_data.items()):
            print(f"  Semi {yr}   : {len(rows)} courses")
        return all_data
    finally:
        conn.close()


def load_winners(db_path: Optional[Path] = None) -> list:
    """
    Retourne les chronos vainqueurs au format :
    [{"r": race_name, "d": "42K"|"21K"|"10K", "y": year,
      "m": men_time_str, "w": women_time_str}, ...]
    """
    conn = _connect(db_path)
    try:
        query = """
            SELECT e.name, e.distance, w.year, w.men_time, w.women_time
            FROM winners w
            JOIN events e ON w.event_id = e.id
            ORDER BY e.name, w.year
        """
        results = conn.execute(query).fetchall()
        rows = []
        for r in results:
            m = r["men_time"] or ""
            w = r["women_time"] or ""
            if not m and not w:
                continue
            dist_key = _DIST_MAP_WINNERS.get(r["distance"], "AUTRE")
            rows.append({
                "r": r["name"],
                "d": dist_key,
                "y": r["year"],
                "m": m,
                "w": w,
            })
        print(f"  Winners    : {len(rows)} resultats")
        return rows
    finally:
        conn.close()


def load_sporthive_avg(db_path: Optional[Path] = None) -> list:
    """
    Retourne les temps moyens Sporthive au format :
    [{"race": name, "year": year, "avg": "HH:MM:SS"}, ...]
    """
    conn = _connect(db_path)
    try:
        query = """
            SELECT e.name, a.year, a.avg_time
            FROM avg_times a
            JOIN events e ON a.event_id = e.id
            WHERE a.source = 'sporthive_api' AND a.avg_time IS NOT NULL
            ORDER BY e.name, a.year
        """
        results = conn.execute(query).fetchall()
        rows = [{"race": r["name"], "year": r["year"], "avg": r["avg_time"]}
                for r in results]
        print(f"  Sporthive avg: {len(rows)} temps moyens")
        return rows
    finally:
        conn.close()


def build_times_db(md: dict, sd: dict, sp_avg: list) -> dict:
    """
    Construit le dictionnaire TIMES_DB au format :
    {race_name_lower: {"men": str, "women": str, "avg": str, "yr": int}, ...}

    Exactement le meme algorithme que l'ancien build_times_db de generate_dashboard.py.
    """
    db = {}
    all_e = []
    for rows in md.values():
        all_e.extend(rows)
    for rows in sd.values():
        all_e.extend(rows)
    all_e.extend(sp_avg)
    all_e.sort(key=lambda x: x.get("year", 0))
    for row in all_e:
        if row.get("avg") or row.get("men"):
            db[row["race"].lower()] = {
                "men": row.get("men") or "",
                "women": row.get("women") or "",
                "avg": row.get("avg") or "",
                "yr": row.get("year"),
            }
    return db


def load_all(db_path: Optional[Path] = None):
    """
    Point d'entree unique : charge toutes les donnees et retourne un tuple
    (finishers, biggest, marathon_data, semi_data, times_db, winners, sporthive_avg)
    directement exploitable par generate_html().
    """
    finishers = load_finishers(db_path)
    biggest = load_biggest(db_path)
    md = {yr: load_marathon(yr, db_path) for yr in [2024, 2025, 2026]}
    sd = load_semi(db_path)
    sp_avg = load_sporthive_avg(db_path)
    tdb = build_times_db(md, sd, sp_avg)
    winners = load_winners(db_path)
    return finishers, biggest, md, sd, tdb, winners, sp_avg
