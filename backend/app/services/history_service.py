from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.session import SessionLocal
from app.models.analysis import Analysis
from app.schemas.history import HistoryEntry, HistoryListResponse
from app.schemas.parcel import ParcelPublic
from app.schemas.prediction import PredictionResponse

logger = logging.getLogger(__name__)


class HistoryService:
    def __init__(self, settings: Settings, db: Session | None = None) -> None:
        self.settings = settings
        self.db = db
        self._lock = Lock()
        self.store_path = self._resolve_store_path()
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self._migration_done = False

    def _resolve_store_path(self) -> Path:
        return self.settings.root_dir / "backend" / "data" / "history_store.json"

    def _session(self) -> Session:
        if self.db is not None:
            return self.db
        return SessionLocal()

    def _read_all(self) -> dict[str, list[dict]]:
        if not self.store_path.exists():
            return {}
        with self.store_path.open("r", encoding="utf-8") as handle:
            try:
                return json.load(handle)
            except json.JSONDecodeError:
                return {}

    def _parse_datetime(self, value: str | None) -> datetime:
        if not value:
            return datetime.now(timezone.utc)
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now(timezone.utc)

    def _run_migrations(self) -> None:
        """Lazy migration - only runs once on first access."""
        if self._migration_done:
            return
        session = self._session()
        should_close = self.db is None
        try:
            existing = session.scalar(select(Analysis.id).limit(1))
            if existing:
                self._migration_done = True
                return

            payload = self._read_all()
            migrated = False
            for user_id, items in payload.items():
                for item in items:
                    try:
                        entry = HistoryEntry.model_validate(item)
                    except Exception:
                        continue

                    prediction = entry.prediction
                    if prediction is None:
                        continue

                    session.add(
                        Analysis(
                            id=entry.analysis_id or str(uuid4()),
                            user_id=user_id,
                            parcel_id=entry.parcel_id,
                            image_name=entry.image_name,
                            image_path=entry.image_path,
                            model_name=prediction.model_name,
                            status=prediction.status,
                            confidence=prediction.confidence,
                            soil_score=prediction.score or 0,
                            refused=prediction.refused,
                            refusal_reason=prediction.refusal_reason,
                            payload_json=prediction.model_dump_json(),
                            created_at=self._parse_datetime(item.get("created_at")),
                        )
                    )
                    migrated = True

            if migrated:
                session.commit()
            self._migration_done = True
        finally:
            if should_close:
                session.close()

    def add_entry(
        self,
        user_id: str,
        prediction: PredictionResponse,
        parcel_id: str | None = None,
        image_name: str | None = None,
        image_url: str | None = None,
        image_path: str | None = None,
        analysis_id: str | None = None,
    ) -> HistoryEntry:
        final_analysis_id = analysis_id or prediction.analysis_id or str(uuid4())
        prediction = prediction.model_copy(update={"analysis_id": final_analysis_id, "image_name": image_name or prediction.image_name, "image_url": image_url or prediction.image_url})
        entry = HistoryEntry(
            id=final_analysis_id,
            user_id=user_id,
            parcel_id=parcel_id,
            image_name=image_name or prediction.image_name,
            image_path=image_path,
            image_url=image_url or prediction.image_url,
            analysis_id=final_analysis_id,
            created_at=prediction.timestamp,
            predictions=prediction.prediction,
            probabilities=prediction.probabilities,
            confidence=prediction.confidence,
            score=prediction.score or 0,
            advice=prediction.field_advice or prediction.recommendation_message or prediction.recommendation,
            refused=prediction.refused,
            refusal_reason=prediction.refusal_reason,
            prediction=prediction,
        )

        session = self._session()
        should_close = self.db is None
        try:
            db_analysis = Analysis(
                id=final_analysis_id,
                user_id=user_id,
                parcel_id=parcel_id,
                image_name=image_name or prediction.image_name,
                image_path=image_path,
                model_name=prediction.model_name,
                status=prediction.status,
                confidence=prediction.confidence,
                soil_score=prediction.score or 0,
                refused=prediction.refused,
                refusal_reason=prediction.refusal_reason,
                payload_json=prediction.model_dump_json(),
                created_at=prediction.timestamp,
            )
            session.add(db_analysis)
            session.commit()
            logger.info(f"[History] Analyse sauvegardée: id={final_analysis_id}, user={user_id}, parcel={parcel_id}, status={prediction.status}")
        except Exception as e:
            logger.error(f"[History] Erreur sauvegarde analyse {final_analysis_id}: {e}", exc_info=True)
            if should_close:
                session.rollback()
            raise
        finally:
            if should_close:
                session.close()

        return entry

    def list_entries(
        self,
        user_id: str,
        parcel_id: str | None = None,
        parcel_lookup: dict[str, ParcelPublic] | None = None,
    ) -> HistoryListResponse:
        session = self._session()
        should_close = self.db is None
        try:
            query = select(Analysis).where(Analysis.user_id == user_id).order_by(Analysis.created_at.desc())
            if parcel_id:
                query = query.where(Analysis.parcel_id == parcel_id)

            rows = session.scalars(query).all()
            entries = [self._to_entry(row, parcel_lookup) for row in rows]
            return HistoryListResponse(user_id=user_id, total=len(entries), entries=entries)
        finally:
            if should_close:
                session.close()

    def get_entry(
        self,
        user_id: str,
        analysis_id: str,
        parcel_lookup: dict[str, ParcelPublic] | None = None,
    ) -> HistoryEntry | None:
        session = self._session()
        should_close = self.db is None
        try:
            row = session.scalar(select(Analysis).where(Analysis.user_id == user_id, Analysis.id == analysis_id))
            if row is None:
                return None
            return self._to_entry(row, parcel_lookup)
        finally:
            if should_close:
                session.close()

    def get_entry_by_id(
        self,
        analysis_id: str,
        user_id: str | None = None,
        parcel_lookup: dict[str, ParcelPublic] | None = None,
    ) -> HistoryEntry | None:
        session = self._session()
        should_close = self.db is None
        try:
            query = select(Analysis).where(Analysis.id == analysis_id)
            if user_id:
                query = query.where(Analysis.user_id == user_id)
            row = session.scalar(query)
            if row is None:
                return None
            return self._to_entry(row, parcel_lookup)
        finally:
            if should_close:
                session.close()

    def _to_entry(self, row: Analysis, parcel_lookup: dict[str, ParcelPublic] | None) -> HistoryEntry:
        prediction = PredictionResponse.model_validate_json(row.payload_json)
        parcel = parcel_lookup.get(row.parcel_id) if parcel_lookup and row.parcel_id else None
        return HistoryEntry(
            id=row.id,
            user_id=row.user_id,
            parcel_id=row.parcel_id,
            parcel=parcel,
            image_name=row.image_name,
            image_path=row.image_path,
            image_url=f"/history/images/{row.id}" if row.image_path else None,
            analysis_id=row.id,
            created_at=row.created_at,
            predictions=prediction.prediction,
            probabilities=prediction.probabilities,
            confidence=prediction.confidence,
            score=row.soil_score,
            advice=prediction.field_advice or prediction.recommendation_message or prediction.recommendation,
            refused=prediction.refused,
            refusal_reason=prediction.refusal_reason,
            prediction=prediction,
        )
