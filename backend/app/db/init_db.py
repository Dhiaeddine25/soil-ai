from __future__ import annotations

from sqlalchemy import inspect

from app.db.base import Base
from app.db.session import engine
from app.models.parcel import Parcel  # noqa: F401
from app.models.user import User  # noqa: F401


def _ensure_parcel_columns() -> None:
    inspector = inspect(engine)
    if "parcels" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("parcels")}
    statements = []

    if "latitude" not in existing_columns:
        statements.append("ALTER TABLE parcels ADD COLUMN latitude REAL")
    if "longitude" not in existing_columns:
        statements.append("ALTER TABLE parcels ADD COLUMN longitude REAL")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.exec_driver_sql(statement)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_parcel_columns()
