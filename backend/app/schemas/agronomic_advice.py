from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


PriorityLevel = Literal['high', 'moderate', 'low']
SoilLevel = Literal['satisfaisant', 'moyen', 'à surveiller', 'critique']


class NutrientAdvice(BaseModel):
    nutrient: Literal['K', 'N', 'P']
    level: str
    priority: PriorityLevel
    advice: str
    soil_status: str
    summary: str
    warning: str


class GlobalAgronomicAdvice(BaseModel):
    soil_score: int
    soil_level: SoilLevel
    soil_status: str
    priority_focus: Literal['K', 'N', 'P']
    priority_summary: str
    summary: str
    warning: str


class AgronomicAdvice(BaseModel):
    potassium: NutrientAdvice
    nitrogen: NutrientAdvice
    phosphorus: NutrientAdvice
    global_advice: GlobalAgronomicAdvice