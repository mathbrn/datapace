"""
DataPace Pydantic Models
========================
Validation stricte des donnees entrantes pour garantir la qualite.
"""
from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
import re

from .config import DISTANCES, is_suspicious_round


class FinisherEntry(BaseModel):
    """Une cellule de finishers dans la grille evenement x annee."""
    race: str = Field(min_length=1)
    distance: Literal["MARATHON", "SEMI", "10KM", "AUTRE"]
    city: str = ""
    period: str = ""
    year: int = Field(ge=2000, le=2030)
    count: Optional[int] = None
    special: Optional[Literal["annule", "elite", "x"]] = None
    source: str = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    @field_validator("count")
    @classmethod
    def reject_suspicious_rounds(cls, v):
        if v is not None and is_suspicious_round(v):
            raise ValueError(
                f"Chiffre rond suspect ({v}). "
                f"Verifier qu'il ne s'agit pas d'un cap d'inscription."
            )
        return v


class WinnerTime(BaseModel):
    """Temps d'un vainqueur H ou F pour une edition donnee."""
    race: str = Field(min_length=1)
    distance: str
    year: int = Field(ge=1950, le=2030)
    men_time: Optional[str] = None
    women_time: Optional[str] = None

    @field_validator("men_time", "women_time")
    @classmethod
    def validate_time_format(cls, v):
        if v is None or v in ("", "N/A", "Annule", "Annulé"):
            return None
        if not re.match(r"^\d{1,2}:\d{2}:\d{2}$", v):
            raise ValueError(f"Format de temps invalide: {v} (attendu HH:MM:SS)")
        return v


class AvgTimeEntry(BaseModel):
    """Temps moyen d'une course pour une edition."""
    race: str = Field(min_length=1)
    year: int = Field(ge=2000, le=2030)
    avg_time: Optional[str] = None
    men_time: Optional[str] = None
    women_time: Optional[str] = None
    source: str = ""


class CrawlResult(BaseModel):
    """Resultat brut d'un crawl API (Sporthive, Tracx, Athlinks...)."""
    source: Literal["sporthive", "tracx", "athlinks", "rtrt", "timeto", "mikatiming", "marathonview"]
    event_name: str = Field(min_length=1)
    race_name: str = ""
    distance_m: int = Field(ge=0)
    date: str = ""
    year: int = Field(ge=0)
    finishers: int = Field(ge=0)
    avg_time: Optional[str] = None
    country: str = ""

    @field_validator("finishers")
    @classmethod
    def reject_virtual_or_tiny(cls, v):
        if v < 50:
            raise ValueError(f"Trop peu de finishers ({v}), probablement virtual ou erreur.")
        return v


class EventMetadata(BaseModel):
    """Metadata complete d'un evenement dans la BDD."""
    id: Optional[int] = None
    name: str = Field(min_length=1)
    city: str = ""
    country: str = ""
    distance: str = ""
    period: str = ""
    badge: Literal["WMM", "ASO", "Autre"] = "Autre"
    first_edition_year: Optional[int] = None
    created_before_2000: bool = False
