from __future__ import annotations

from app.schemas.prediction_quality import QualityCheck


class RefusalService:
    def human_message(self, quality_check: QualityCheck) -> str:
        return 'Cette image ne permet pas une estimation fiable du sol.'

    def tips(self) -> list[str]:
        return [
            'reprendre la photo',
            'meilleure lumière',
            'rapprocher le sol',
            'éviter les ombres',
            'éviter objets parasites',
        ]

    def _issue_label(self, issue: str) -> str:
        mapping = {
            'empty_file': 'fichier vide',
            'invalid_image': 'image invalide',
            'image_too_small': 'image trop petite',
            'too_dark': 'image trop sombre',
            'too_bright': 'image trop claire',
            'low_contrast': 'contraste faible',
            'blurry': 'image floue',
            'poor_soil_presence': 'mauvaise présence de sol',
            'bad_framing': 'mauvais cadrage',
        }
        return mapping.get(issue, issue)
