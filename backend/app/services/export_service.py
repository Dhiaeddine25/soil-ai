from __future__ import annotations

import csv
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.schemas.history import HistoryListResponse


class ExportService:
    def build_csv(self, history: HistoryListResponse) -> str:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "user_id",
            "parcel_id",
            "parcel_name",
            "analysis_id",
            "created_at",
            "model_name",
            "confidence",
            "K_level",
            "N_level",
            "P_level",
            "interpretation",
            "recommendation",
            "source",
            "model_status",
        ])

        for entry in history.entries:
            prediction = entry.prediction
            parcel_name = entry.parcel.name if entry.parcel else (entry.parcel_id or "")
            writer.writerow([
                entry.user_id,
                entry.parcel_id or "",
                parcel_name,
                entry.analysis_id,
                entry.created_at.isoformat(),
                prediction.model_name,
                f"{prediction.confidence:.4f}",
                prediction.prediction.K_level,
                prediction.prediction.N_level,
                prediction.prediction.P_level,
                prediction.interpretation,
                prediction.recommendation,
                prediction.source,
                prediction.model_status,
            ])

        return buffer.getvalue()

    def build_pdf(self, history: HistoryListResponse) -> bytes:
        buffer = io.BytesIO()
        document = SimpleDocTemplate(buffer, pagesize=A4, title=f"SoilAI History - {history.user_id}")
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(f"SoilAI - Suivi parcellaire", styles["Title"]))
        story.append(Paragraph(f"Utilisateur: {history.user_id}", styles["Heading2"]))
        story.append(Paragraph(f"Nombre d'analyses: {history.total}", styles["BodyText"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(
            "Export de suivi parcellaire pour la soutenance: pre-diagnostic indicatif, recommandations prudentes, et confirmation laboratoire si necessaire.",
            styles["BodyText"],
        ))
        story.append(Spacer(1, 12))

        table_data = [["Date", "Parcelle", "ID", "K", "N", "P", "Confiance", "Mode"]]
        for entry in history.entries:
            prediction = entry.prediction
            parcel_name = entry.parcel.name if entry.parcel else (entry.parcel_id or "")
            table_data.append([
                entry.created_at.strftime("%Y-%m-%d %H:%M"),
                parcel_name,
                entry.parcel_id or "",
                prediction.prediction.K_level,
                prediction.prediction.N_level,
                prediction.prediction.P_level,
                f"{prediction.confidence:.0%}",
                prediction.model_status,
            ])

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b241d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7b99d")),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(table)
        story.append(Spacer(1, 16))
        story.append(Paragraph("Rappel: le resultat est une estimation rapide et orientative. Le laboratoire reste la reference quand une confirmation est requise.", styles["Italic"]))

        document.build(story)
        return buffer.getvalue()
