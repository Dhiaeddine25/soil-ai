from __future__ import annotations

from app.db.session import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.parcel import ParcelCreate, ParcelPublic, ParcelUpdate
from app.services.parcel_service import ParcelService
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session


router = APIRouter(tags=["parcels"])


def get_parcel_service(db: Session = Depends(get_db)) -> ParcelService:
    return ParcelService(db)


@router.get("/parcels", response_model=list[ParcelPublic])
def list_parcels(
    current_user: User = Depends(get_current_user),
    parcel_service: ParcelService = Depends(get_parcel_service),
) -> list[ParcelPublic]:
    return parcel_service.list_for_user(current_user.id)


@router.post("/parcels", response_model=ParcelPublic, status_code=status.HTTP_201_CREATED)
def create_parcel(
    payload: ParcelCreate,
    current_user: User = Depends(get_current_user),
    parcel_service: ParcelService = Depends(get_parcel_service),
) -> ParcelPublic:
    return parcel_service.create(current_user.id, payload)


@router.get("/parcels/{parcel_id}", response_model=ParcelPublic)
def get_parcel(
    parcel_id: str,
    current_user: User = Depends(get_current_user),
    parcel_service: ParcelService = Depends(get_parcel_service),
) -> ParcelPublic:
    parcel = parcel_service.get_for_user(parcel_id, current_user.id)
    if not parcel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parcel not found")
    return parcel_service._to_public(parcel)


@router.patch("/parcels/{parcel_id}", response_model=ParcelPublic)
def update_parcel(
    parcel_id: str,
    payload: ParcelUpdate,
    current_user: User = Depends(get_current_user),
    parcel_service: ParcelService = Depends(get_parcel_service),
) -> ParcelPublic:
    parcel = parcel_service.update(parcel_id, current_user.id, payload)
    if not parcel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parcel not found")
    return parcel


@router.delete("/parcels/{parcel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parcel(
    parcel_id: str,
    current_user: User = Depends(get_current_user),
    parcel_service: ParcelService = Depends(get_parcel_service),
) -> Response:
    deleted = parcel_service.delete(parcel_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parcel not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)