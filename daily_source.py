from __future__ import annotations
from dataclasses import dataclass
from typing import List

MIN_YR_SAMPLES_FOR_DAILY_SUMMARY = 18  # Jedno, absolutne źródło prawdy

@dataclass(frozen=True)
class DailyPick:
    hp: List[dict]          # lista godzin użyta do summary
    marker: str             # "" albo " *" (fallback)
    source: str             # "yrno" / "openmeteo" / "mixed"

def _hours_for_date(hours: List[dict], source: str, date_str: str) -> List[dict]:
    return [h for h in hours if h.get("source") == source and h.get("time_local", "").startswith(date_str)]

def pick_hours_for_daily_summary(hours: List[dict], daily_diag: dict, date_str: str) -> DailyPick:
    diag = daily_diag.get(date_str, {})
    n_yr = int(diag.get("n_yr", 0))
    
    hy_day = _hours_for_date(hours, "yrno", date_str)
    ho_day = _hours_for_date(hours, "openmeteo", date_str)
    
    # 1) Preferuj Yr.no tylko jeśli ma sensowną rozdzielczość
    if n_yr >= MIN_YR_SAMPLES_FOR_DAILY_SUMMARY and len(hy_day) >= 6:
        return DailyPick(hp=hy_day, marker="", source="yrno")
        
    # 2) Fallback: Open-Meteo
    if ho_day:
        return DailyPick(hp=ho_day, marker=" *", source="openmeteo")
        
    # 3) Ostatnia deska ratunku: cokolwiek z hours
    mixed = [h for h in hours if h.get("time_local", "").startswith(date_str)]
    return DailyPick(hp=mixed, marker=" *", source="mixed")