from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from app.core.config import Settings
from app.schemas.parcel import ParcelPublic
from app.schemas.history import HistoryEntry, HistoryListResponse
from app.schemas.prediction import PredictionResponse


class HistoryService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store_path = self._resolve_store_path()
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _resolve_store_path(self) -> Path:
        return self.settings.root_dir / "backend" / "data" / "history_store.json"

    def _read_all(self) -> dict[str, list[dict]]:
        if not self.store_path.exists():
            return {}
        with self.store_path.open("r", encoding="utf-8") as handle:
            try:
                return json.load(handle)
            except json.JSONDecodeError:
                return {}

    def _write_all(self, payload: dict[str, list[dict]]) -> None:
        with self.store_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)

    def add_entry(
        self,
        user_id: str,
        prediction: PredictionResponse,
        parcel_id: str | None = None,
        image_name: str | None = None,
    ) -> HistoryEntry:
        entry = HistoryEntry(
            user_id=user_id,
            parcel_id=parcel_id,
            image_name=image_name,
            analysis_id=str(uuid4()),
            created_at=datetime.now(timezone.utc),
            prediction=prediction,
        )

        with self._lock:
            payload = self._read_all()
            payload.setdefault(user_id, [])
            payload[user_id].insert(0, json.loads(entry.model_dump_json()))
            self._write_all(payload)

        return entry

    def list_entries(
        self,
        user_id: str,
        parcel_id: str | None = None,
        parcel_lookup: dict[str, ParcelPublic] | None = None,
    ) -> HistoryListResponse:
        payload = self._read_all()
        raw_entries = payload.get(user_id, [])
        entries = []
        for item in raw_entries:
            entry = HistoryEntry.model_validate(item)
            if parcel_id and entry.parcel_id != parcel_id:
                continue
            if parcel_lookup and entry.parcel_id:
                parcel = parcel_lookup.get(entry.parcel_id)
                if parcel is not None and entry.parcel is None:
                    entry = entry.model_copy(update={"parcel": parcel})
            entries.append(entry)
        return HistoryListResponse(user_id=user_id, total=len(entries), entries=entries)

    def get_entry(
        self,
        user_id: str,
        analysis_id: str,
        parcel_lookup: dict[str, ParcelPublic] | None = None,
    ) -> HistoryEntry | None:
        payload = self._read_all()
        raw_entries = payload.get(user_id, [])
        for item in raw_entries:
            entry = HistoryEntry.model_validate(item)
            if entry.analysis_id != analysis_id:
                continue
            if parcel_lookup and entry.parcel_id:
                parcel = parcel_lookup.get(entry.parcel_id)
                if parcel is not None and entry.parcel is None:
                    entry = entry.model_copy(update={"parcel": parcel})
            return entry
        return None
