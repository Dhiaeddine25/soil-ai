from __future__ import annotations


class InterpretationService:
    def build_interpretation(self, prediction: dict[str, str], confidence: float) -> str:
        base = (
            f"Indicative NPK estimate: {prediction['K_level']} / {prediction['N_level']} / {prediction['P_level']}."
        )
        if confidence >= 0.85:
            return base + " Strong signal for a field pre-diagnosis."
        if confidence >= 0.7:
            return base + " Useful to guide action, with lab confirmation if the stakes are high."
        return base + " Exploratory result that should be confirmed by laboratory analysis."

    def build_recommendation(self, confidence: float) -> str:
        if confidence >= 0.85:
            return "Indicative result is robust; follow-up monitoring is still recommended before final action."
        if confidence >= 0.7:
            return "Monitoring is recommended; lab confirmation is advised depending on agronomic context."
        return "Laboratory confirmation is strongly recommended before any fertilization decision."
