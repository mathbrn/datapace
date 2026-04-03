"""
Tests unitaires — Configuration
=================================
Verifie les constantes et la detection de chiffres ronds.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datapace.config import is_suspicious_round, ASO_KEYWORDS, WMM_KEYWORDS, DISTANCES


def test_round_numbers_detected():
    assert is_suspicious_round(10000) is True
    assert is_suspicious_round(20000) is True
    assert is_suspicious_round(50000) is True
    assert is_suspicious_round(100000) is True


def test_non_round_numbers_ok():
    assert is_suspicious_round(10001) is False
    assert is_suspicious_round(42195) is False
    assert is_suspicious_round(15234) is False
    assert is_suspicious_round(0) is False


def test_aso_keywords_present():
    assert len(ASO_KEYWORDS) > 0
    assert "schneider electric" in ASO_KEYWORDS


def test_wmm_keywords_present():
    assert len(WMM_KEYWORDS) == 7  # 7 WMM races
    assert "boston marathon" in WMM_KEYWORDS


def test_distances():
    assert "MARATHON" in DISTANCES
    assert "SEMI" in DISTANCES
    assert "10KM" in DISTANCES
    assert "AUTRE" in DISTANCES
