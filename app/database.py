from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


def ensure_sqlite_schema() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "products" not in inspector.get_table_names():
        return

    columns = {column_info["name"] for column_info in inspector.get_columns("products")}
    with engine.connect() as connection:
        if "code" not in columns:
            connection.execute(text('ALTER TABLE products ADD COLUMN code VARCHAR(50)'))
            connection.commit()
        if "lot_number" not in columns:
            connection.execute(text('ALTER TABLE products ADD COLUMN lot_number VARCHAR(100)'))
            connection.commit()


ensure_sqlite_schema()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
