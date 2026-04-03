"""
Tests unitaires — Modeles Pydantic
===================================
Verifie la validation des donnees entrantes.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datapace.models import FinisherEntry, WinnerTime, CrawlResult, AvgTimeEntry


class TestFinisherEntry:
    """Tests pour la validation des finishers."""

    def test_valid_entry(self):
        entry = FinisherEntry(race="TCS London Marathon", distance="MARATHON",
                              year=2024, count=45000)  # not round
        assert entry.count == 45000

    def test_reject_round_10000(self):
        with pytest.raises(Exception, match="Chiffre rond suspect"):
            FinisherEntry(race="Test", distance="MARATHON", year=2024, count=10000)

    def test_reject_round_50000(self):
        with pytest.raises(Exception, match="Chiffre rond suspect"):
            FinisherEntry(race="Test", distance="SEMI", year=2024, count=50000)

    def test_accept_non_round(self):
        entry = FinisherEntry(race="Test", distance="10KM", year=2024, count=10001)
        assert entry.count == 10001

    def test_accept_none_count(self):
        entry = FinisherEntry(race="Test", distance="MARATHON", year=2024, count=None)
        assert entry.count is None

    def test_special_annule(self):
        entry = FinisherEntry(race="Test", distance="MARATHON", year=2020,
                              special="annule")
        assert entry.special == "annule"

    def test_invalid_distance(self):
        with pytest.raises(Exception):
            FinisherEntry(race="Test", distance="ULTRA", year=2024, count=100)

    def test_year_too_low(self):
        with pytest.raises(Exception):
            FinisherEntry(race="Test", distance="MARATHON", year=1999, count=100)

    def test_year_too_high(self):
        with pytest.raises(Exception):
            FinisherEntry(race="Test", distance="MARATHON", year=2031, count=100)

    def test_empty_race_rejected(self):
        with pytest.raises(Exception):
            FinisherEntry(race="", distance="MARATHON", year=2024, count=100)


class TestWinnerTime:
    """Tests pour la validation des chronos vainqueurs."""

    def test_valid_times(self):
        w = WinnerTime(race="Berlin", distance="42K", year=2023,
                       men_time="2:01:09", women_time="2:11:53")
        assert w.men_time == "2:01:09"
        assert w.women_time == "2:11:53"

    def test_na_becomes_none(self):
        w = WinnerTime(race="Berlin", distance="42K", year=2023,
                       men_time="N/A", women_time="Annule")
        assert w.men_time is None
        assert w.women_time is None

    def test_invalid_format_rejected(self):
        with pytest.raises(Exception, match="Format de temps invalide"):
            WinnerTime(race="Berlin", distance="42K", year=2023,
                       men_time="2h01m09s")

    def test_none_times_ok(self):
        w = WinnerTime(race="Berlin", distance="42K", year=2023)
        assert w.men_time is None
        assert w.women_time is None


class TestCrawlResult:
    """Tests pour la validation des resultats de crawl."""

    def test_valid_result(self):
        r = CrawlResult(source="sporthive", event_name="Amsterdam Marathon",
                        distance_m=42195, year=2024, finishers=15000)
        assert r.finishers == 15000

    def test_reject_too_few_finishers(self):
        with pytest.raises(Exception, match="Trop peu de finishers"):
            CrawlResult(source="tracx", event_name="Test", distance_m=42195,
                        year=2024, finishers=10)

    def test_invalid_source(self):
        with pytest.raises(Exception):
            CrawlResult(source="unknown_api", event_name="Test",
                        distance_m=42195, year=2024, finishers=1000)

    def test_empty_event_name_rejected(self):
        with pytest.raises(Exception):
            CrawlResult(source="sporthive", event_name="",
                        distance_m=42195, year=2024, finishers=1000)


class TestAvgTimeEntry:
    """Tests pour les temps moyens."""

    def test_valid(self):
        e = AvgTimeEntry(race="Paris Marathon", year=2024, avg_time="4:12:33")
        assert e.avg_time == "4:12:33"

    def test_minimal(self):
        e = AvgTimeEntry(race="Test", year=2024)
        assert e.avg_time is None
