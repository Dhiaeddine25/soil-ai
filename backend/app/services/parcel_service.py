from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.parcel import Parcel
from app.schemas.parcel import ParcelCreate, ParcelPublic, ParcelUpdate


class ParcelService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _to_public(self, parcel: Parcel) -> ParcelPublic:
        return ParcelPublic(
            id=parcel.id,
            user_id=parcel.user_id,
            name=parcel.name,
            location=parcel.location,
            latitude=parcel.latitude,
            longitude=parcel.longitude,
            created_at=parcel.created_at,
        )

    def list_for_user(self, user_id: str) -> list[ParcelPublic]:
        parcels = self.db.scalars(
            select(Parcel).where(Parcel.user_id == user_id).order_by(Parcel.created_at.desc())
        ).all()
        return [self._to_public(parcel) for parcel in parcels]

    def get_for_user(self, parcel_id: str, user_id: str) -> Parcel | None:
        return self.db.scalar(select(Parcel).where(Parcel.id == parcel_id, Parcel.user_id == user_id))

    def create(self, user_id: str, payload: ParcelCreate) -> ParcelPublic:
        location = payload.location.strip() if payload.location else None
        parcel = Parcel(
            id=str(uuid4()),
            user_id=user_id,
            name=payload.name.strip(),
            location=location,
            latitude=payload.latitude if location else None,
            longitude=payload.longitude if location else None,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(parcel)
        self.db.commit()
        self.db.refresh(parcel)
        return self._to_public(parcel)

    def update(self, parcel_id: str, user_id: str, payload: ParcelUpdate) -> ParcelPublic | None:
        parcel = self.get_for_user(parcel_id, user_id)
        if not parcel:
            return None

        if payload.name is not None:
            parcel.name = payload.name.strip()
        if payload.location is not None:
            parcel.location = payload.location.strip() or None
            parcel.latitude = payload.latitude if parcel.location else None
            parcel.longitude = payload.longitude if parcel.location else None
        elif payload.latitude is not None or payload.longitude is not None:
            parcel.latitude = payload.latitude
            parcel.longitude = payload.longitude

        self.db.commit()
        self.db.refresh(parcel)
        return self._to_public(parcel)

    def delete(self, parcel_id: str, user_id: str) -> bool:
        parcel = self.get_for_user(parcel_id, user_id)
        if not parcel:
            return False

        self.db.delete(parcel)
        self.db.commit()
        return True