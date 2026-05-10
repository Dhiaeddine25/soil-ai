from __future__ import annotations

from collections.abc import Mapping

from app.core.config import Settings
from app.schemas.prediction import NutrientPrediction
from app.schemas.prediction_quality import ConfidenceDetails, PredictionStatus, QualityCheck


class PredictionDecisionService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def build_confidence_details(self, probabilities: Mapping[str, float]) -> ConfidenceDetails:
        ranked = sorted((float(value), label) for label, value in probabilities.items())
        if ranked:
            max_prob, top_label = ranked[-1]
            second_prob = ranked[-2][0] if len(ranked) > 1 else 0.0
        else:
            max_prob = 0.0
            second_prob = 0.0
            top_label = None

        margin = max_prob - second_prob
        top_group = top_label[0] if top_label else None
        return ConfidenceDetails(
            max_prob=round(max_prob, 4),
            second_prob=round(second_prob, 4),
            margin=round(max(margin, 0.0), 4),
            top_label=top_label,
            top_group=top_group,
        )

    def determine_status(self, quality_check: QualityCheck, confidence: float, confidence_details: ConfidenceDetails) -> PredictionStatus:
        if not quality_check.valid:
            return 'image_non_exploitable'
        if confidence_details.max_prob < self.settings.trust_confirm_confidence_min or confidence_details.margin < self.settings.trust_confirm_margin_min:
            return 'prediction_incertaine'
        if confidence_details.max_prob < self.settings.trust_ok_confidence_min or confidence_details.margin < self.settings.trust_ok_margin_min:
            return 'confirmation_recommandee'
        return 'ok'

    def can_trust(self, status: PredictionStatus) -> bool:
        return status in {'ok', 'confirmation_recommandee'}

    def warning_message(self, status: PredictionStatus, quality_check: QualityCheck) -> str:
        if status == 'image_non_exploitable':
            reason = ', '.join(quality_check.issues) if quality_check.issues else 'qualité insuffisante'
            return f"Image non exploitable: {reason}. Reprendre une image plus nette, plus lisible et mieux exposée."
        if status == 'prediction_incertaine':
            return 'Prédiction incertaine: les scores sont trop proches ou trop bas pour une lecture fiable.'
        if status == 'confirmation_recommandee':
            return 'Confirmation recommandée: le résultat est exploitable mais mérite une validation terrain ou laboratoire.'
        return 'Résultat exploitable pour un pré-diagnostic indicatif.'

    def recommendation_message(self, status: PredictionStatus) -> str:
        if status == 'image_non_exploitable':
            return 'Reprendre une image mieux cadrée, plus nette et plus contrastée avant de relancer l’analyse.'
        if status == 'prediction_incertaine':
            return 'Relancer l’analyse avec une image plus lisible ou compléter par une confirmation externe.'
        if status == 'confirmation_recommandee':
            return 'Résultat utilisable avec prudence: confirmer avant toute décision agronomique définitive.'
        return 'Résultat jugé suffisamment robuste pour un pré-diagnostic indicatif.'

    def result_summary(self, status: PredictionStatus, prediction: NutrientPrediction | None) -> str:
        if status == 'image_non_exploitable' or prediction is None:
            return 'L’image ne permet pas une interprétation fiable.'
        return f"Classe NPK retenue: {prediction.K_level} / {prediction.N_level} / {prediction.P_level}."