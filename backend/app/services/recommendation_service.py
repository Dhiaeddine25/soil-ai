from __future__ import annotations


class RecommendationService:
    def build(self, status: str, focus: str | None = None) -> str:
        if status == 'image_non_exploitable':
            return 'Reprendre une photo plus nette et relancer l analyse.'
        if status == 'prediction_incertaine':
            return 'Resultat incertain: refaire une photo ou verifier sur le terrain.'
        if status == 'confirmation_recommandee':
            return 'Resultat utilisable avec prudence: confirmation recommandee.'
        if focus:
            return f"Priorite de surveillance: {focus}."
        return 'Resultat indicatif, a confronter au terrain.'
