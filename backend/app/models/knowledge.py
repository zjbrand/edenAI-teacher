# backend/app/models/knowledge.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text

from app.db import Base


class KnowledgeDoc(Base):
  __tablename__ = "knowledge_docs"

  id = Column(Integer, primary_key=True, index=True)

  # 元のファイル名（一覧表示用）
  original_name = Column(String, nullable=False)

  # 以前はローカルファイルの保存名に使っていたが、
  # 今回は DB 運用に切り替えるので「オプション扱い」にしておく
  stored_name = Column(String, nullable=True)

  size = Column(Integer, nullable=False, default=0)
  content_type = Column(String, nullable=True)

  # ★ 実際のナレッジ本文（テキスト）を DB に保存
  content = Column(Text, nullable=False)

  # 将来用：active / deleted など
  status = Column(String, nullable=False, default="active")

  created_at = Column(DateTime, default=datetime.utcnow)
  updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
