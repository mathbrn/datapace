"""
Tests unitaires — Data Loader SQLite
======================================
Verifie que le data loader retourne les formats attendus par le dashboard JS.
"""
import pytest
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datapace.database import init_db, get_db, get_or_create_event, upsert_finisher, upsert_winner, upsert_avg_time
from datapace.data_loader import (
    load_finishers, load_biggest, load_marathon, load_semi,
    load_winners, load_sporthive_avg, build_times_db, load_all,
)


@pytest.fixture
def populated_db():
    """Cree une BDD avec des donnees de test."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = Path(f.name)
    init_db(path)

    with get_db(path) as conn:
        # Evenement marathon WMM
        eid1 = get_or_create_event(conn, "TCS London Marathon", "MARATHON",
                                   "London", "Avril", "WMM")
        upsert_finisher(conn, eid1, 2023, 48832, source="test", skip_existing=False)
        upsert_finisher(conn, eid1, 2024, 53926, source="test", skip_existing=False)
        upsert_finisher(conn, eid1, 2025, 56640, source="test", skip_existing=False)
        upsert_winner(conn, eid1, 2024, "2:04:48", "2:16:16", source="test")
        upsert_avg_time(conn, eid1, 2024, avg_time="4:32:10",
                        men_time="4:15:00", women_time="4:50:00", source="excel_marathon")

        # Evenement semi ASO
        eid2 = get_or_create_event(conn, "Hoka Semi de Paris", "SEMI",
                                   "Paris", "Mars", "ASO")
        upsert_finisher(conn, eid2, 2024, 40000, source="test", skip_existing=False)
        upsert_finisher(conn, eid2, 2025, 42000, source="test", skip_existing=False)
        upsert_avg_time(conn, eid2, 2025, avg_time="1:58:00", source="excel_semi")

        # Evenement avec edition annulee
        eid3 = get_or_create_event(conn, "Test Marathon", "MARATHON",
                                   "TestCity", "Juin", "Autre")
        upsert_finisher(conn, eid3, 2020, -1, source="test", skip_existing=False)
        upsert_finisher(conn, eid3, 2024, 5000, source="test", skip_existing=False)

        # Sporthive avg time
        upsert_avg_time(conn, eid1, 2023, avg_time="4:35:00", source="sporthive_api")

    yield path
    path.unlink(missing_ok=True)


class TestLoadFinishers:
    def test_returns_list(self, populated_db):
        rows = load_finishers(populated_db)
        assert isinstance(rows, list)
        assert len(rows) >= 3

    def test_format_keys(self, populated_db):
        rows = load_finishers(populated_db)
        london = [r for r in rows if "London" in r["r"]][0]
        # Toutes les cles attendues par le JS
        assert "p" in london  # period
        assert "c" in london  # city
        assert "d" in london  # distance
        assert "r" in london  # race name
        assert "y3" in london  # 2023
        assert "y4" in london  # 2024
        assert "y5" in london  # 2025
        assert "y6" in london  # 2026
        assert "hist" in london  # historique
        assert "fy" in london  # first year

    def test_values(self, populated_db):
        rows = load_finishers(populated_db)
        london = [r for r in rows if "London" in r["r"]][0]
        assert london["y3"] == 48832
        assert london["y4"] == 53926
        assert london["y5"] == 56640
        assert london["d"] == "MARATHON"
        assert london["c"] == "London"

    def test_cancelled_edition(self, populated_db):
        rows = load_finishers(populated_db)
        test = [r for r in rows if "Test Marathon" in r["r"]][0]
        assert test["hist"].get(2020) == -1


class TestLoadBiggest:
    def test_returns_list(self, populated_db):
        rows = load_biggest(populated_db)
        assert isinstance(rows, list)
        assert len(rows) >= 1

    def test_format(self, populated_db):
        rows = load_biggest(populated_db)
        row = rows[0]
        assert "c" in row
        assert "r" in row
        assert "hist" in row


class TestLoadMarathon:
    def test_returns_data(self, populated_db):
        rows = load_marathon(2024, populated_db)
        assert isinstance(rows, list)
        assert len(rows) >= 1

    def test_format(self, populated_db):
        rows = load_marathon(2024, populated_db)
        row = rows[0]
        assert "race" in row
        assert "avg" in row
        assert "year" in row
        assert row["year"] == 2024


class TestLoadSemi:
    def test_returns_dict(self, populated_db):
        data = load_semi(populated_db)
        assert isinstance(data, dict)
        assert 2025 in data

    def test_format(self, populated_db):
        data = load_semi(populated_db)
        row = data[2025][0]
        assert "race" in row
        assert "avg" in row
        assert row["year"] == 2025


class TestLoadWinners:
    def test_returns_list(self, populated_db):
        rows = load_winners(populated_db)
        assert isinstance(rows, list)
        assert len(rows) >= 1

    def test_format(self, populated_db):
        rows = load_winners(populated_db)
        row = rows[0]
        assert "r" in row  # race name
        assert "d" in row  # distance (42K/21K/10K)
        assert "y" in row  # year
        assert "m" in row  # men time
        assert "w" in row  # women time

    def test_distance_mapping(self, populated_db):
        rows = load_winners(populated_db)
        london = [r for r in rows if "London" in r["r"]][0]
        assert london["d"] == "42K"  # MARATHON → 42K


class TestLoadSporthiveAvg:
    def test_returns_sporthive_only(self, populated_db):
        rows = load_sporthive_avg(populated_db)
        assert isinstance(rows, list)
        assert len(rows) >= 1
        assert all("race" in r and "year" in r and "avg" in r for r in rows)


class TestBuildTimesDb:
    def test_produces_dict(self, populated_db):
        md = {2024: load_marathon(2024, populated_db)}
        sd = load_semi(populated_db)
        sp = load_sporthive_avg(populated_db)
        tdb = build_times_db(md, sd, sp)
        assert isinstance(tdb, dict)
        # Au moins une entree avec les bonnes cles
        key = list(tdb.keys())[0]
        assert "avg" in tdb[key]
        assert "men" in tdb[key]
        assert "women" in tdb[key]
        assert "yr" in tdb[key]


class TestLoadAll:
    def test_returns_all_components(self, populated_db):
        finishers, biggest, md, sd, tdb, winners, sp_avg = load_all(populated_db)
        assert isinstance(finishers, list) and len(finishers) > 0
        assert isinstance(biggest, list)
        assert isinstance(md, dict) and 2024 in md
        assert isinstance(sd, dict)
        assert isinstance(tdb, dict)
        assert isinstance(winners, list) and len(winners) > 0
        assert isinstance(sp_avg, list)
