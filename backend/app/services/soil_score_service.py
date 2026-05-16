from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SoilScore:
    score: int
    level: str
    status: str


class SoilScoreService:
    def compute(self, high_count: int, moderate_count: int, low_count: int) -> SoilScore:
        score = max(0, min(100, 100 - (high_count * 25) - (moderate_count * 12) - (low_count * 4)))
        if score >= 80:
            level = 'bon'
            status = 'bon'
        elif score >= 60:
            level = 'acceptable'
            status = 'acceptable'
        elif score >= 40:
            level = 'à surveiller'
            status = 'à surveiller'
        else:
            level = 'critique'
            status = 'critique'
        return SoilScore(score=score, level=level, status=status)
