"""
DataPace Configuration
======================
Centralise tous les chemins, constantes et secrets du projet.
Les secrets sont lus depuis les variables d'environnement (fichier .env).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT  # Excel + JSON sont a la racine pour l'instant

load_dotenv(PROJECT_ROOT / ".env")

FILES = {
    "finishers":     DATA_DIR / "Suivi_Finishers_Monde_10k_-_21k_-_42k_HISTORIQUE.xlsx",
    "marathon_2024": DATA_DIR / "Temps_moyen_par_marathon_2024.xlsx",
    "marathon_2025": DATA_DIR / "Temps_moyen_par_marathon_2025.xlsx",
    "marathon_2026": DATA_DIR / "Temps_moyen_par_marathon_2026.xlsx",
    "semi":          DATA_DIR / "Temps_moyen_semi-marathon.xlsx",
    "winners":       DATA_DIR / "Chronos_Vainqueurs.xlsx",
}

OUTPUT_FILE = DATA_DIR / "datapace_dashboard.html"
DB_FILE = DATA_DIR / "datapace.db"
UNIFIED_DB = DATA_DIR / "unified_race_database.json"

# ── API Secrets (from .env) ──────────────────────────────────────────────────
TRACX_TOKEN = os.environ.get("TRACX_TOKEN", "")
RTRT_APPID = os.environ.get("RTRT_APPID", "")
RTRT_TOKEN = os.environ.get("RTRT_TOKEN", "")
WA_API_KEY = os.environ.get("WA_API_KEY", "")

# ── Constants ────────────────────────────────────────────────────────────────
YEAR_MIN = 2000
YEAR_MAX = 2030

DISTANCES = ("MARATHON", "SEMI", "10KM", "AUTRE")

ASO_KEYWORDS = [
    "schneider electric", "hoka semi de paris", "semi de paris",
    "run in lyon", "beaujolais", "adidas 10k paris", "10k montmartre",
    "cancer research", "asics ldnx", "adidas manchester",
]

WMM_KEYWORDS = [
    "tcs new york city marathon", "tcs london marathon", "boston marathon",
    "tcs sydney marathon", "bmw berlin marathon",
    "bank of america chicago marathon", "tokyo marathon",
]

# ── Validation ───────────────────────────────────────────────────────────────
ROUND_NUMBER_THRESHOLDS = {10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 100000}


def is_suspicious_round(count: int) -> bool:
    """Return True if a finisher count looks like a round cap/estimate."""
    return count in ROUND_NUMBER_THRESHOLDS
