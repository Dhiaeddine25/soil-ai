from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserPublic


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _to_public(self, user: User) -> UserPublic:
        return UserPublic(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at,
        )

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email.lower().strip()))

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def register(self, payload: UserCreate) -> TokenResponse:
        email = payload.email.lower().strip()
        if self.get_by_email(email):
            raise ValueError("Email already registered")

        user = User(
            id=str(uuid4()),
            email=email,
            full_name=payload.full_name.strip() if payload.full_name else None,
            hashed_password=hash_password(payload.password),
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        token = create_access_token(user.id)
        return TokenResponse(access_token=token, user=self._to_public(user))

    def login(self, payload: UserLogin) -> TokenResponse:
        user = self.get_by_email(payload.email.lower().strip())
        if not user or not verify_password(payload.password, user.hashed_password):
            raise ValueError("Invalid credentials")

        token = create_access_token(user.id)
        return TokenResponse(access_token=token, user=self._to_public(user))
