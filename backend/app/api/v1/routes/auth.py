from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_current_user, get_user_service
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserPublic
from app.services.user_service import UserService


router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=TokenResponse)
def register(payload: UserCreate, user_service: UserService = Depends(get_user_service)) -> TokenResponse:
    try:
        return user_service.register(payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: UserLogin, user_service: UserService = Depends(get_user_service)) -> TokenResponse:
    try:
        return user_service.login(payload)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")


@router.get("/auth/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
    )


@router.post("/auth/logout")
def logout() -> dict:
    return {"status": "ok"}
