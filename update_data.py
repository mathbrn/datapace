#!/usr/bin/env python3
"""
DataPace — Point d'entree unique pour alimenter la base de donnees.
===================================================================
Remplace update_finishers.py comme methode principale.
Ecrit dans SQLite ET dans l'Excel (retrocompatibilite).

Usage:
    # Ajouter/mettre a jour des finishers
    python update_data.py finisher "TCS London Marathon" MARATHON 2024 45012

    # Ajouter un temps vainqueur
    python update_data.py winner "BMW Berlin Marathon" MARATHON 2024 "2:01:09" "2:16:42"

    # Ajouter un temps moyen
    python update_data.py avgtime "Paris Marathon" MARATHON 2024 "4:12:33"

    # Regenerer le dashboard apres mise a jour
    python update_data.py dashboard
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from datapace.config import DB_FILE, ASO_KEYWORDS, WMM_KEYWORDS
from datapace.database import init_db, get_db, get_or_create_event, upsert_finisher, upsert_winner, upsert_avg_time

# Support DB path override
_DB_PATH = Path(os.environ.get("DATAPACE_DB", str(DB_FILE)))


def detect_badge(name: str) -> str:
    low = name.lower()
    if any(k in low for k in WMM_KEYWORDS):
        return "WMM"
    if any(k in low for k in ASO_KEYWORDS):
        return "ASO"
    return "Autre"


def cmd_finisher(args):
    """Ajoute un finisher count dans la BDD + Excel."""
    if len(args) < 4:
        print("Usage: python update_data.py finisher \"Race Name\" DISTANCE YEAR COUNT")
        print("  DISTANCE: MARATHON, SEMI, 10KM, AUTRE")
        print("  COUNT: nombre entier, ou 'x', '-', 'Elite'")
        sys.exit(1)

    race, distance, year, count_str = args[0], args[1], int(args[2]), args[3]

    if distance not in ("MARATHON", "SEMI", "10KM", "AUTRE"):
        print(f"ERREUR: Distance '{distance}' invalide.")
        sys.exit(1)

    # Parse special values
    special_map = {"x": None, "-": -1, "elite": -2}
    if count_str.strip().lower() in special_map:
        count = special_map[count_str.strip().lower()]
    else:
        count = int(count_str)

    # 1) Ecrire dans SQLite
    init_db(_DB_PATH)
    with get_db(_DB_PATH) as conn:
        badge = detect_badge(race)
        event_id = get_or_create_event(conn, race, distance, badge=badge)

        if count is None:
            # 'x' = event did not exist → pas de ligne en BDD
            print(f"[SKIP] '{race}' {year}: marque comme inexistant (x), pas d'entree BDD.")
        else:
            result = upsert_finisher(conn, event_id, year, count, source="manual")
            if result:
                print(f"[SQLite OK] {race} ({distance}) {year}: {count}")
            else:
                print(f"[SQLite SKIP] {race} ({distance}) {year}: deja rempli, pas de modification.")

    # 2) Ecrire dans Excel aussi (retrocompatibilite)
    try:
        from update_finishers import update as excel_update
        excel_update(race, distance, year, count_str)
    except Exception as e:
        print(f"[Excel WARN] Echec ecriture Excel: {e}")
        print("  La donnee est sauvegardee dans la BDD SQLite.")


def cmd_winner(args):
    """Ajoute un temps vainqueur."""
    if len(args) < 4:
        print('Usage: python update_data.py winner "Race" DISTANCE YEAR "H:MM:SS" ["H:MM:SS"]')
        sys.exit(1)

    race, distance, year = args[0], args[1], int(args[2])
    men_time = args[3] if len(args) > 3 else None
    women_time = args[4] if len(args) > 4 else None

    if men_time in ("", "-", "N/A", "None"):
        men_time = None
    if women_time in ("", "-", "N/A", "None"):
        women_time = None

    init_db(_DB_PATH)
    with get_db(_DB_PATH) as conn:
        badge = detect_badge(race)
        event_id = get_or_create_event(conn, race, distance, badge=badge)
        upsert_winner(conn, event_id, year, men_time, women_time, source="manual")
        print(f"[OK] Winner {race} {year}: H={men_time or '-'} F={women_time or '-'}")


def cmd_avgtime(args):
    """Ajoute un temps moyen."""
    if len(args) < 4:
        print('Usage: python update_data.py avgtime "Race" DISTANCE YEAR "H:MM:SS"')
        sys.exit(1)

    race, distance, year = args[0], args[1], int(args[2])
    avg_time = args[3]

    init_db(_DB_PATH)
    with get_db(_DB_PATH) as conn:
        badge = detect_badge(race)
        event_id = get_or_create_event(conn, race, distance, badge=badge)
        upsert_avg_time(conn, event_id, year, avg_time=avg_time, source="manual")
        print(f"[OK] Avg time {race} {year}: {avg_time}")


def cmd_dashboard(_args):
    """Regenere le dashboard depuis la BDD."""
    print("Regeneration du dashboard...")
    # Import ici pour eviter import circulaire
    from generate_dashboard import main as gen_main
    gen_main()


def cmd_stats(_args):
    """Affiche les statistiques de la BDD."""
    from datapace.database import get_stats
    init_db(_DB_PATH)
    stats = get_stats(_DB_PATH)
    print("\n── DataPace Database Stats ──")
    print(f"  Evenements     : {stats['events']}")
    print(f"  Finishers      : {stats['finisher_entries']} entrees")
    print(f"  Winners        : {stats['winner_entries']} entrees")
    print(f"  Temps moyens   : {stats['avg_time_entries']} entrees")
    print(f"  Crawl log      : {stats['crawl_log_entries']} entrees")
    if stats.get("sources"):
        print("  Sources:")
        for src, cnt in stats["sources"].items():
            print(f"    {src}: {cnt}")
    print()


COMMANDS = {
    "finisher": cmd_finisher,
    "winner": cmd_winner,
    "avgtime": cmd_avgtime,
    "dashboard": cmd_dashboard,
    "stats": cmd_stats,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("DataPace — Mise a jour des donnees")
        print("=" * 40)
        print("\nCommandes disponibles:")
        print("  finisher  \"Race\" DISTANCE YEAR COUNT    Ajouter des finishers")
        print("  winner    \"Race\" DISTANCE YEAR H F      Ajouter temps vainqueur")
        print("  avgtime   \"Race\" DISTANCE YEAR TIME     Ajouter temps moyen")
        print("  dashboard                                Regenerer le dashboard")
        print("  stats                                    Afficher les stats BDD")
        print("\nExemples:")
        print('  python update_data.py finisher "TCS London Marathon" MARATHON 2024 45012')
        print('  python update_data.py winner "BMW Berlin Marathon" MARATHON 2024 "2:01:09" "2:16:42"')
        print('  python update_data.py dashboard')
        sys.exit(0)

    cmd = sys.argv[1]
    COMMANDS[cmd](sys.argv[2:])


if __name__ == "__main__":
    main()
