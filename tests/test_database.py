"""
Tests unitaires — Base de donnees
===================================
Teste le schema, CRUD, et les regles metier (SKIP, upsert).
"""
import pytest
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datapace.database import init_db, get_db, get_or_create_event, upsert_finisher, upsert_winner, upsert_avg_time, get_stats


@pytest.fixture
def db_path():
    """Cree une BDD temporaire pour chaque test."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = Path(f.name)
    init_db(path)
    yield path
    path.unlink(missing_ok=True)


class TestSchema:
    def test_tables_created(self, db_path):
        with get_db(db_path) as conn:
            tables = [r["name"] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()]
        assert "events" in tables
        assert "finishers" in tables
        assert "winners" in tables
        assert "avg_times" in tables
        assert "crawl_log" in tables

    def test_idempotent_init(self, db_path):
        # Running init twice should not fail
        init_db(db_path)
        init_db(db_path)


class TestEvents:
    def test_create_event(self, db_path):
        with get_db(db_path) as conn:
            eid = get_or_create_event(conn, "TCS London Marathon", "MARATHON", "London", "Avril", "WMM")
            assert eid > 0

    def test_get_existing_event(self, db_path):
        with get_db(db_path) as conn:
            eid1 = get_or_create_event(conn, "Berlin Marathon", "MARATHON")
            eid2 = get_or_create_event(conn, "Berlin Marathon", "MARATHON")
            assert eid1 == eid2

    def test_different_events_different_ids(self, db_path):
        with get_db(db_path) as conn:
            eid1 = get_or_create_event(conn, "Paris Marathon", "MARATHON")
            eid2 = get_or_create_event(conn, "Lyon Marathon", "MARATHON")
            assert eid1 != eid2


class TestFinishers:
    def test_insert_finisher(self, db_path):
        with get_db(db_path) as conn:
            eid = get_or_create_event(conn, "Test Race", "MARATHON")
            result = upsert_finisher(conn, eid, 2024, 42000, source="test")
            assert result is True

    def test_skip_existing(self, db_path):
        """La regle SKIP : ne jamais ecraser une cellule deja remplie."""
        with get_db(db_path) as conn:
            eid = get_or_create_event(conn, "Test Race", "MARATHON")
            upsert_finisher(conn, eid, 2024, 42000, source="original")
            # Attempt to overwrite — should be skipped
            result = upsert_finisher(conn, eid, 2024, 99999, source="new", skip_existing=True)
            assert result is False
            # Verify original value is preserved
            row = conn.execute(
                "SELECT count FROM finishers WHERE event_id = ? AND year = ?",
                (eid, 2024)
            ).fetchone()
            assert row["count"] == 42000

    def test_force_overwrite(self, db_path):
        """Avec skip_existing=False, on peut forcer la mise a jour."""
        with get_db(db_path) as conn:
            eid = get_or_create_event(conn, "Test Race", "MARATHON")
            upsert_finisher(conn, eid, 2024, 42000, skip_existing=False)
            upsert_finisher(conn, eid, 2024, 43000, source="updated", skip_existing=False)
            row = conn.execute(
                "SELECT count FROM finishers WHERE event_id = ? AND year = ?",
                (eid, 2024)
            ).fetchone()
            assert row["count"] == 43000

    def test_cancelled_edition(self, db_path):
        with get_db(db_path) as conn:
            eid = get_or_create_event(conn, "Test Race", "MARATHON")
            upsert_finisher(conn, eid, 2020, -1, source="excel", skip_existing=False)
            row = conn.execute(
                "SELECT count FROM finishers WHERE event_id = ? AND year = ?",
                (eid, 2020)
            ).fetchone()
            assert row["count"] == -1


class TestWinners:
    def test_insert_winner(self, db_path):
        with get_db(db_path) as conn:
            eid = get_or_create_event(conn, "Berlin Marathon", "MARATHON")
            upsert_winner(conn, eid, 2023, "2:01:09", "2:11:53", source="test")
            row = conn.execute(
                "SELECT men_time, women_time FROM winners WHERE event_id = ? AND year = ?",
                (eid, 2023)
            ).fetchone()
            assert row["men_time"] == "2:01:09"
            assert row["women_time"] == "2:11:53"

    def test_upsert_preserves_existing(self, db_path):
        """COALESCE: si on met a jour avec NULL, garde l'ancienne valeur."""
        with get_db(db_path) as conn:
            eid = get_or_create_event(conn, "Test", "MARATHON")
            upsert_winner(conn, eid, 2023, "2:01:09", "2:11:53")
            upsert_winner(conn, eid, 2023, None, "2:10:00")  # only update women
            row = conn.execute(
                "SELECT men_time, women_time FROM winners WHERE event_id = ? AND year = ?",
                (eid, 2023)
            ).fetchone()
            assert row["men_time"] == "2:01:09"  # preserved
            assert row["women_time"] == "2:10:00"  # updated


class TestStats:
    def test_stats_empty_db(self, db_path):
        stats = get_stats(db_path)
        assert stats["events"] == 0
        assert stats["finisher_entries"] == 0
