from __future__ import annotations

import csv
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
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
        document = SimpleDocTemplate(buffer, pagesize=A4, title=f"SoilAI Report - {history.user_id}", topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        brand = colors.HexColor("#2b241d")
        accent = colors.HexColor("#5b7d5e")
        light = colors.HexColor("#f7f4ef")

        title_style = ParagraphStyle("Title", parent=styles["Title"], textColor=brand, fontSize=20, spaceAfter=4)
        subtitle_style = ParagraphStyle("Subtitle", parent=styles["BodyText"], textColor=colors.HexColor("#6b5f4b"), fontSize=10)
        section_style = ParagraphStyle("Section", parent=styles["Heading3"], textColor=brand, fontSize=12, spaceBefore=12, spaceAfter=6)
        body_style = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10, leading=14)
        muted_style = ParagraphStyle("Muted", parent=styles["BodyText"], fontSize=9, textColor=colors.HexColor("#7a6f5c"))

        story = []
        latest = history.entries[0] if history.entries else None
        parcel = latest.parcel if latest and latest.parcel else None
        prediction = latest.prediction if latest else None

        header_table = Table([
            [Paragraph("SoilAI", title_style), Paragraph("Rapport de suivi parcellaire", subtitle_style)],
            [Paragraph(f"Utilisateur: {history.user_id}", muted_style), Paragraph(datetime.now().strftime("%d/%m/%Y"), muted_style)],
        ], colWidths=[260, 260])
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TEXTCOLOR", (0, 0), (0, 0), brand),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 12))

        story.append(Paragraph("Synthese", section_style))
        summary_text = (
            f"Nombre d'analyses: {history.total}. "
            "Ce rapport fournit un resume indicatif pour un suivi terrain rapide."
        )
        story.append(Paragraph(summary_text, body_style))

        story.append(Paragraph("Parcelle", section_style))
        parcel_rows = [
            ["Nom", parcel.name if parcel else (latest.parcel_id if latest else "-")],
            ["Localisation", parcel.location if parcel and parcel.location else "-"],
            ["Region", parcel.region if parcel and parcel.region else "-"],
            ["Surface (ha)", f"{parcel.area_ha:.2f}" if parcel and parcel.area_ha else "-"],
            ["Culture", parcel.crop if parcel and parcel.crop else "-"],
        ]
        parcel_table = Table(parcel_rows, colWidths=[140, 380])
        parcel_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), light),
            ("TEXTCOLOR", (0, 0), (-1, -1), brand),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9cbb6")),
        ]))
        story.append(parcel_table)
        story.append(Spacer(1, 10))

        story.append(Paragraph("Analyse courante", section_style))
        if prediction and prediction.prediction:
            npk_row = [
                ["Date", latest.created_at.strftime("%d/%m/%Y %H:%M")],
                ["Etat global", prediction.agronomic_advice.global_advice.soil_status if prediction.agronomic_advice else "-"],
                ["Score sante", f"{prediction.agronomic_advice.global_advice.soil_score}/100" if prediction.agronomic_advice else "-"],
                ["Confiance", f"{prediction.confidence:.0%}"],
                ["Niveau N", prediction.prediction.N_level],
                ["Niveau P", prediction.prediction.P_level],
                ["Niveau K", prediction.prediction.K_level],
                ["Image", latest.image_name or "-"],
            ]
            analysis_table = Table(npk_row, colWidths=[140, 380])
            analysis_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), light),
                ("TEXTCOLOR", (0, 0), (-1, -1), brand),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9cbb6")),
            ]))
            story.append(analysis_table)
        else:
            story.append(Paragraph("Analyse non disponible.", body_style))

        story.append(Paragraph("Conseil terrain intelligent", section_style))
        if prediction and prediction.field_advice:
            story.append(Paragraph(prediction.field_advice, body_style))
        else:
            story.append(Paragraph("Conseil non disponible pour cette analyse.", body_style))
        story.append(Paragraph("Analyse indicative basee sur une image.", muted_style))

        story.append(Paragraph("Timeline courte", section_style))
        timeline_entries = history.entries[:3]
        if timeline_entries:
            timeline_data = [["Date", "Etat", "Score", "Confiance"]]
            for entry in timeline_entries:
                pred = entry.prediction
                status = pred.agronomic_advice.global_advice.soil_status if pred.agronomic_advice else "-"
                score = pred.agronomic_advice.global_advice.soil_score if pred.agronomic_advice else 0
                timeline_data.append([
                    entry.created_at.strftime("%d/%m/%Y"),
                    status,
                    f"{score}/100",
                    f"{pred.confidence:.0%}",
                ])
            timeline_table = Table(timeline_data, repeatRows=1)
            timeline_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), brand),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7b99d")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ]))
            story.append(timeline_table)
        else:
            story.append(Paragraph("Aucune analyse precedente.", body_style))

        story.append(Spacer(1, 14))
        story.append(Paragraph(
            "Ce rapport est une aide de terrain. Aucun dosage ni prescription definitive n'est fourni.",
            muted_style,
        ))

        document.build(story)
        return buffer.getvalue()
