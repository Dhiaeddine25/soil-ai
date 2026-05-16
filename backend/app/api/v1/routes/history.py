from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
import mimetypes
from pathlib import Path

from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.core.config import Settings, get_settings
from app.services.parcel_service import ParcelService
from app.models.user import User
from app.services.export_service import ExportService
from app.schemas.history import HistoryEntry, HistoryListResponse
from app.services.history_service import HistoryService


router = APIRouter(tags=["history"])


@router.get("/history/users/{user_id}", response_model=HistoryListResponse)
def get_history(
    user_id: str,
    parcel_id: str | None = None,
    settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HistoryListResponse:
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    service = HistoryService(settings, db)
    parcel_lookup = {parcel.id: parcel for parcel in ParcelService(db).list_for_user(current_user.id)}
    return service.list_entries(user_id, parcel_id=parcel_id, parcel_lookup=parcel_lookup)


@router.get("/history/{analysis_id}", response_model=HistoryEntry)
def get_history_entry(
    analysis_id: str,
    settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HistoryEntry:
    history_service = HistoryService(settings, db)
    parcel_lookup = {parcel.id: parcel for parcel in ParcelService(db).list_for_user(current_user.id)}
    entry = history_service.get_entry_by_id(analysis_id, user_id=current_user.id, parcel_lookup=parcel_lookup)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return entry


@router.get("/history/images/{analysis_id}")
def get_history_image(
    analysis_id: str,
    settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    history_service = HistoryService(settings, db)
    entry = history_service.get_entry_by_id(analysis_id, user_id=current_user.id)
    if not entry or not entry.image_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    image_path = Path(entry.image_path)
    if not image_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    media_type = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
    return StreamingResponse(image_path.open("rb"), media_type=media_type)


@router.get("/history/{user_id}/export/csv")
def export_history_csv(
    user_id: str,
    parcel_id: str | None = None,
    settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    history_service = HistoryService(settings, db)
    export_service = ExportService()
    parcel_lookup = {parcel.id: parcel for parcel in ParcelService(db).list_for_user(current_user.id)}
    history = history_service.list_entries(user_id, parcel_id=parcel_id, parcel_lookup=parcel_lookup)
    csv_content = export_service.build_csv(history)
    filename = f"soilai_history_{user_id}.csv"
    return StreamingResponse(
        iter([csv_content.encode("utf-8-sig")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/history/{user_id}/export/pdf")
def export_history_pdf(
    user_id: str,
    parcel_id: str | None = None,
    settings: Settings = Depends(get_settings),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    history_service = HistoryService(settings, db)
    export_service = ExportService()
    parcel_lookup = {parcel.id: parcel for parcel in ParcelService(db).list_for_user(current_user.id)}
    history = history_service.list_entries(user_id, parcel_id=parcel_id, parcel_lookup=parcel_lookup)
    pdf_bytes = export_service.build_pdf(history)
    filename = f"soilai_history_{user_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
