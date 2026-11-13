"""
CryoGuard Database Configuration
=================================
Sets up the SQLAlchemy engine, session factory, and declarative base.
Uses a local SQLite file at ~/.cryoguard/cryoguard.db so the app is fully
self-contained and works offline on any machine.
"""
from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Ensure the data directory exists so the DB file can be created.
DATA_DIR: Path = Path.home() / ".cryoguard"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'cryoguard.db'}"

# SQLite needs check_same_thread=False so FastAPI's async handlers can
# reuse the same connection across threads without errors.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base — all our models inherit from this.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a fresh DB session per request and
    closes it (and the connection) when the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()