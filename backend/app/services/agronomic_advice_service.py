from __future__ import annotations

from collections.abc import Mapping

from app.schemas.agronomic_advice import AgronomicAdvice, GlobalAgronomicAdvice, NutrientAdvice, PriorityLevel
from app.schemas.prediction import NutrientPrediction


class AgronomicAdviceService:
    _priority_rank: dict[str, int] = {
        'high': 0,
        'moderate': 1,
        'low': 2,
    }

    _warning = (
        'Ce conseil reste indicatif et provient d’une image. '
        'Il ne donne pas de dose d’engrais: une analyse de laboratoire et un avis agronomique restent nécessaires avant toute décision.'
    )

    def build(self, prediction: NutrientPrediction | Mapping[str, str]) -> AgronomicAdvice:
        potassium = self._build_nutrient_advice('K', self._level_for(prediction, 'K'))
        nitrogen = self._build_nutrient_advice('N', self._level_for(prediction, 'N'))
        phosphorus = self._build_nutrient_advice('P', self._level_for(prediction, 'P'))
        global_advice = self._build_global_advice([potassium, nitrogen, phosphorus])

        return AgronomicAdvice(
            potassium=potassium,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            global_advice=global_advice,
        )

    def _level_for(self, prediction: NutrientPrediction | Mapping[str, str], nutrient: str) -> str:
        key = f'{nutrient}_level'
        if isinstance(prediction, Mapping):
            return str(prediction[key])
        return str(getattr(prediction, key))

    def _build_nutrient_advice(self, nutrient: str, level: str) -> NutrientAdvice:
        priority = self._priority_for_level(nutrient, level)
        soil_status, advice, summary = self._messages_for_level(nutrient, level, priority)
        return NutrientAdvice(
            nutrient=nutrient,
            level=level,
            priority=priority,
            advice=advice,
            soil_status=soil_status,
            summary=summary,
            warning=self._warning,
        )

    def _build_global_advice(self, nutrient_advices: list[NutrientAdvice]) -> GlobalAgronomicAdvice:
        ordered = sorted(nutrient_advices, key=lambda item: self._priority_rank[item.priority])
        highest_priority = ordered[0]
        high_count = sum(1 for item in nutrient_advices if item.priority == 'high')
        moderate_count = sum(1 for item in nutrient_advices if item.priority == 'moderate')
        low_count = sum(1 for item in nutrient_advices if item.priority == 'low')
        soil_score = max(0, min(100, 100 - (high_count * 25) - (moderate_count * 12) - (low_count * 4)))

        if soil_score >= 80:
            soil_level = 'bon'
            soil_status = 'bon'
        elif soil_score >= 60:
            soil_level = 'acceptable'
            soil_status = 'acceptable'
        elif soil_score >= 40:
            soil_level = 'à surveiller'
            soil_status = 'à surveiller'
        else:
            soil_level = 'critique'
            soil_status = 'critique'

        nutrient_names = {'K': 'potassium', 'N': 'azote', 'P': 'phosphore'}
        focus_name = nutrient_names[highest_priority.nutrient]
        remaining = [item for item in ordered[1:]]
        remaining_summary = ', '.join(nutrient_names[item.nutrient] for item in remaining)

        summary = (
            f"État global du sol : {soil_status}. "
            f"Élément principal à surveiller : {focus_name}. "
            f"Les autres nutriments à garder en tête sont {remaining_summary}."
        )

        return GlobalAgronomicAdvice(
            soil_score=soil_score,
            soil_level=soil_level,
            soil_status=soil_status,
            priority_focus=highest_priority.nutrient,
            priority_summary=f"{focus_name.capitalize()} est l’élément principal à surveiller.",
            summary=summary,
            warning=self._warning,
        )

    def _priority_for_level(self, nutrient: str, level: str) -> PriorityLevel:
        if nutrient == 'P':
            return 'high' if level == 'P0' else 'low'
        if level.endswith('0'):
            return 'high'
        if level.endswith('1'):
            return 'moderate'
        return 'low'

    def _messages_for_level(self, nutrient: str, level: str, priority: PriorityLevel) -> tuple[str, str, str]:
        nutrient_names = {'K': 'potassium', 'N': 'azote', 'P': 'phosphore'}
        if priority == 'high':
            return (
                'faible',
                f"Le {nutrient_names[nutrient]} semble faible. Une confirmation en laboratoire est recommandée avant toute correction.",
                f"{nutrient_names[nutrient].capitalize()} à surveiller en priorité.",
            )
        if priority == 'moderate':
            return (
                'moyen',
                f"Le {nutrient_names[nutrient]} est à un niveau moyen. Un suivi régulier suffit pour l’instant, avec confirmation si la décision est sensible.",
                f"{nutrient_names[nutrient].capitalize()} à suivre avec prudence.",
            )
        return (
            'bon',
            f"Le {nutrient_names[nutrient]} paraît correct. Continuez la surveillance sans conclure sur une dose à partir de cette seule image.",
            f"{nutrient_names[nutrient].capitalize()} plutôt rassurant à ce stade.",
        )