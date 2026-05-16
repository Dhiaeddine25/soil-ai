from __future__ import annotations

from collections.abc import Mapping

from app.schemas.agronomic_advice import AgronomicAdvice, GlobalAgronomicAdvice, NutrientAdvice, PriorityLevel
from app.schemas.prediction import NutrientPrediction
from app.services.soil_score_service import SoilScoreService


class AgronomicAdviceService:
    _priority_rank: dict[str, int] = {
        'high': 0,
        'moderate': 1,
        'low': 2,
    }
    _level_rank: dict[str, int] = {
        'K0': 0,
        'K1': 1,
        'K2': 2,
        'N0': 0,
        'N1': 1,
        'N2': 2,
        'P0': 0,
        'P1': 1,
    }
    _field_disclaimer = 'Analyse indicative basee sur une image.'

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

    def field_disclaimer(self) -> str:
        return self._field_disclaimer

    def build_field_advice(
        self,
        advice: AgronomicAdvice,
        confidence: float,
        previous_prediction: NutrientPrediction | Mapping[str, str] | None = None,
        previous_advice: AgronomicAdvice | None = None,
    ) -> tuple[str, str]:
        nutrient_names = {'K': 'potassium', 'N': 'azote', 'P': 'phosphore'}
        focus = advice.global_advice.priority_focus
        focus_name = nutrient_names[focus]
        current_levels = {
            'K': advice.potassium.level,
            'N': advice.nitrogen.level,
            'P': advice.phosphorus.level,
        }
        current_level = current_levels[focus]

        if previous_prediction:
            previous_level = self._level_for(previous_prediction, focus)
            delta = self._compare_levels(previous_level, current_level)
            if delta < 0:
                trend_sentence = f"Le {focus_name} semble plus faible que lors de la derniere analyse."
            elif delta > 0:
                trend_sentence = f"Le {focus_name} s'est ameliore depuis la derniere analyse."
            else:
                trend_sentence = f"Le {focus_name} reste stable par rapport a la derniere analyse."
        else:
            trend_sentence = f"Premiere lecture sur cette parcelle. Le {focus_name} sert de reference initiale."

        score_sentence = ""
        if previous_advice:
            current_score = advice.global_advice.soil_score
            previous_score = previous_advice.global_advice.soil_score
            delta_score = current_score - previous_score
            if delta_score > 0:
                score_sentence = "Le score sante progresse legerement."
            elif delta_score < 0:
                score_sentence = "Le score sante recule legerement."
            else:
                score_sentence = "Le score sante reste stable."

        if confidence < 0.6:
            confidence_sentence = "La confiance reste faible: une verification terrain est recommande."
        elif confidence < 0.75:
            confidence_sentence = "La confiance est moyenne, rester prudent sur les decisions."
        else:
            confidence_sentence = "La confiance est bonne pour un suivi terrain indicatif."

        advice_text = " ".join(part for part in [trend_sentence, score_sentence, confidence_sentence] if part)
        return advice_text.strip(), self._field_disclaimer

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
        score = SoilScoreService().compute(high_count, moderate_count, low_count)

        nutrient_names = {'K': 'potassium', 'N': 'azote', 'P': 'phosphore'}
        focus_name = nutrient_names[highest_priority.nutrient]
        remaining = [item for item in ordered[1:]]
        remaining_summary = ', '.join(nutrient_names[item.nutrient] for item in remaining)

        summary = (
            f"État global du sol : {score.status}. "
            f"Élément principal à surveiller : {focus_name}. "
            f"Les autres nutriments à garder en tête sont {remaining_summary}."
        )

        return GlobalAgronomicAdvice(
            soil_score=score.score,
            soil_level=score.level,
            soil_status=score.status,
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

    def _compare_levels(self, previous_level: str, current_level: str) -> int:
        previous_rank = self._level_rank.get(previous_level, 0)
        current_rank = self._level_rank.get(current_level, 0)
        return current_rank - previous_rank