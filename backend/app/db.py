# backend/app/db.py
from __future__ import annotations

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 環境変数 DATABASE_URL があればそれを優先（本番 / Render 用）
# 例: postgres://USER:PASSWORD@HOST:PORT/DBNAME
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./eden_teacher.db")

# Render の Postgres は "postgres://" 形式が多いので SQLAlchemy 形式に変換
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# SQLite のときだけ check_same_thread が必要
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
